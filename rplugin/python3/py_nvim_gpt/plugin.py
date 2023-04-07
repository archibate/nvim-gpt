import neovim
import contextlib
import threading
import inspect

from .io_tags import Done, Shutdown
from .logging import LogSystem


@neovim.plugin
class GPTPlugin:
    nvim: neovim.Nvim

    def __init__(self, nvim):
        print('GPT plugin started')
        self.nvim = nvim

        self._mutex = threading.Lock()
        self._state = 'idle'  # options: idle, running
        self._cursor_counter = 0
        self._qa_count = 0
        self._stop_count = 0
        self._last_question = None
        self._last_bufnr = None
        self._multiline_was_regenerate = None
        self._multiline_submitted = False
        self._last_range = None
        self._templates = {}

        self._model = 'gpt-3.5-turbo'
        self._params = {}

        self._cursors = '|/_\\'  # '_ ' for blinking '_' and ' '
        self._code_quote = '{question}\n```{filetype}\n{code}\n```'
        self._in_language = '{question}\n(in {filetype})'
        self._question_title = '\n🙂:'
        self._answer_title = '\n🤖:'
        self._regenerate_title = '🔄'
        self._welcome_messages = [
            "This is {}, how can I help you?",
            "Here is {}, how can I help you?",
            "This is {}, any question today?",
            "Here is {}, any question today?",
            "Here is {}, what's the problem?",
            "{}! What's wrong with the code?",
            "{} coming! Need help in coding?",
            "{} is glad to help in your job!",
            "{} here! Looking for some help?",
            "{}! Nice to meet you! Question?",
            "Coding? Worry not, just ask {}!",
            "Coding? Worry not, {} now here!",
            "Coding? That's {}'s speciality!",
            "Bugs? Let {} get your solution!",
            "Anything may {} help? Just ask!",
            "Your true companion, {} coming!",
        ]
        self._window_width = 45
        self._multiline_input_height = 8
        self._window_options = {
            'wrap': True,
            'signcolumn': 'no',
            'list': False,
            'cursorline': True,
            'number': False,
            'relativenumber': False,
            # 'virtualedit': 'onemore',
        }
        self._lock_last_line = 'force'    # options: none, last-char, last-line, force
        self._update_interval = 180       # milliseconds

        self._take_setup_options()

        if not self._templates:
            from .keymaps import preset_templates
            for line in preset_templates.splitlines():
                line = line.strip()
                if not line: continue
                args = line.split(' ')
                assert args[0] == 'GPTTemplate', args[0]
                self._add_gpt_template(args[1], *args[2:])

    def _take_setup_options(self):
        opts = self.nvim.exec_lua("vim.g._gpt_setup_options = require'nvim-gpt'._setup_options")
        opts = self.nvim.eval('g:_gpt_setup_options')
        if opts is None:
            raise RuntimeError("no setup options provided, please add require'nvim-gpt'._setup{} to your init.lua")

        print('setup options:', opts)

        update_keys = [
            'model',
            'params',
            'cursors',
            'code_quote',
            'question_title',
            'answer_title',
            'regenerate_title',
            'window_width',
            'multiline_input_height',
            'lock_last_line',
            'update_interval',
            'window_options',
        ]
        for k in update_keys:
            if k in opts:
                assert hasattr(self, '_' + k), k
                setattr(self, '_' + k, opts[k])

        welcome = opts.get('welcome_messages', 'fancy')
        if welcome != 'fancy':
            self._welcome_messages.clear()
            if welcome != 'none':
                self._welcome_messages = [welcome]

        if 'question_templates' in opts:
            for line in opts['question_templates'].splitlines():
                line = line.strip()
                if not line: continue
                args = line.split(' ')
                assert args[0] == 'GPTTemplate', args[0]
                self._add_gpt_template(args[1], *args[2:])

    def get_bot(self):
        from .workers import get_worker
        return get_worker(self._model, self._params.get(self._model, dict()))

    @neovim.command('GPTModel', nargs='?')  # type: ignore
    def gpt_model(self, args):
        with self._critical_section():
            if not args:
                self.nvim.command('echo "{}"'.format(self._model))
                return
            model = args[0]
            from .workers import available_models
            avail_models = available_models()
            if model in ('prev', 'next'):
                curr_index = avail_models.index(self._model)
                delta = -1 if model == 'prev' else 1
                self._model = avail_models[(curr_index + delta) % len(avail_models)]
                return
            if model not in avail_models:
                self.nvim.command('echo "no such model {}"'.format(model))
                return
            self._model = model

    @neovim.command('GPTLog')
    def gpt_log(self):
        with self._critical_section():
            buffer, _ = self._create_sub_window('GPTLog', width=self._window_width)
            buffer.options['modifiable'] = True
            try:
                buffer[:] = LogSystem.instance().read_log().splitlines()
            finally:
                buffer.options['modifiable'] = False
            self.nvim.command('norm! G')

    def _create_sub_window(self, name, location='belowright', modifiable=False, width=None, height=None, filetype=None, bufhidden='wipe'):
        bufnr = self.nvim.funcs.bufnr(name)
        if bufnr == -1:
            self.nvim.command('{} new'.format(location))
            buffer = self.nvim.current.buffer
            window = self.nvim.current.window
            buffer.name = name
            buffer.options['buftype'] = 'nofile'
            buffer.options['bufhidden'] = bufhidden
            buffer.options['swapfile'] = False
            buffer.options['modifiable'] = modifiable
            if filetype:
                buffer.options['filetype'] = filetype
            if width:
                window.width = width
            if height:
                window.height = height
            return buffer, False
        else:
            winnr = self.nvim.funcs.bufwinnr(bufnr)
            if winnr == -1:
                self.nvim.command('{} split'.format(location))
                self.nvim.command('buffer ' + str(bufnr))
                window = self.nvim.current.window
                if width:
                    window.width = width
                if height:
                    window.height = height
            else:
                if self.nvim.funcs.bufnr('%') == bufnr:
                    buffer = self.nvim.buffers[bufnr]
                    return buffer, True
                self.nvim.command(str(winnr) + 'windo buffer')
            buffer = self.nvim.buffers[bufnr]
            return buffer, False

    @neovim.command('GPTOpen')
    def gpt_open(self):
        with self._critical_section():
            self._do_gpt_open()

    @neovim.command('GPTClose')
    def gpt_close(self):
        with self._critical_section():
            for name in ('GPT', 'GPTInput', 'GPTLog'):
                bufnr = self.nvim.funcs.bufnr(name)
                if bufnr != -1:
                    winnr = self.nvim.funcs.bufwinnr(bufnr)
                    if winnr != -1:
                        self.nvim.command(str(winnr) + 'wincmd q')

    @neovim.command('GPTToggle')
    def gpt_toggle(self):
        with self._critical_section():
            self._do_gpt_open(toggle=True)

    def _do_gpt_open(self, toggle=False):
        bufnr = self.nvim.funcs.bufnr("GPT")
        if bufnr == -1:
            self.nvim.command('rightbelow vnew')
            buffer = self.nvim.current.buffer
            window = self.nvim.current.window
            buffer.name = 'GPT'
            buffer.options['buftype'] = 'nofile'
            buffer.options['filetype'] = 'markdown'
            buffer.options['bufhidden'] = 'hide'
            buffer.options['modifiable'] = False
            buffer.options['swapfile'] = False
            window.width = self._window_width
            for k, v in self._window_options.items():
                window.options[k] = v
            self._set_welcome_message()
            from .keymaps import gpt_window_keymaps
            for line in gpt_window_keymaps.splitlines():
                line = line.strip()
                if line:
                    self.nvim.command(line)
        elif toggle:
            winnr = self.nvim.funcs.bufwinnr(bufnr)
            if winnr == -1:
                self.nvim.command('rightbelow vsplit')
                self.nvim.command('buffer ' + str(bufnr))
            else:
                self.nvim.command(str(winnr) + 'wincmd q')
        else:
            winnr = self.nvim.funcs.bufwinnr(bufnr)
            if winnr == -1:
                self.nvim.command('rightbelow vsplit')
                self.nvim.command('buffer ' + str(bufnr))
                self.nvim.current.window.width = self._window_width
            else:
                self.nvim.command(str(winnr) + 'windo buffer')

    @neovim.command('GPTMultiline', nargs='*')  # type: ignore
    def gpt_multiline(self, args):  # plan: (I)nput
        with self._critical_section():
            self._do_gpt_multiline(' '.join(args))

    def _do_gpt_multiline(self, exist_question, regenerate=False):
        buffer, reused = self._create_sub_window('GPTInput', modifiable=True, height=self._multiline_input_height, filetype='markdown', bufhidden='hide')
        if reused:
            question = '\n'.join(buffer[:])
            self.nvim.command('wincmd q')
            self._do_gpt_open()
            self._submit_question(question, regenerate=self._multiline_was_regenerate or False)
            self._multiline_submitted = True
            self._multiline_was_regenerate = None
        else:
            self._multiline_was_regenerate = regenerate
            # if not exist_question.strip() and self._last_question:
            #     exist_question = self._last_question
            if exist_question.strip():
                buffer[:] = exist_question.split('\n')
            elif self._multiline_submitted:
                self._multiline_submitted = False
                buffer[:] = []
            from .keymaps import gpt_multiline_edit_keymaps
            bufnr = self.nvim.funcs.bufnr('%')
            for line in gpt_multiline_edit_keymaps.format(bufnr=bufnr).splitlines():
                line = line.strip()
                if line: self.nvim.command(line)
            # print('nimadir', dir(self.nvim))
            if len(buffer[0]):
                self.nvim.command('stopinsert')
                if not regenerate:
                    self.nvim.feedkeys('gH', 'n')
            else:
                self.nvim.command('startinsert')
            if self.nvim.funcs.exists('b:_no_enter_submit'):
                self.nvim.command('unlet b:_no_enter_submit')

    @neovim.command('GPTDiscard')
    def gpt_discard(self):  # plan: (d)iscard
        with self._critical_section():
            self._do_gpt_open()
            self._do_gpt_reset()

    def _do_gpt_reset(self):
        self._do_gpt_stop()
        self._qa_count = 0
        self._set_welcome_message()
        bot = self.get_bot()
        bot.push_reset()

    @neovim.command('GPTStop')
    def gpt_stop(self):  # plan: (s)top
        with self._critical_section():
            self._do_gpt_stop()

    def _do_gpt_stop(self):
        if self._state == 'running':
            self._stop_count += 1
            self._rid_last_line_cursor()
            self._transit_state('idle')

    @neovim.command('GPT', nargs='*')  # type: ignore
    def gpt_input(self, args):  # plan: <CR> (i)nput
        with self._critical_section():
            question = self._compose_question(args)
            self._do_gpt_stop()
            self._do_gpt_open()
            if not args:
                self._do_gpt_multiline('')
                return
            self._submit_question(question)

    @neovim.command('GPTWrite', nargs='*', range=True)  # type: ignore
    def gpt_write(self, args, range_):  # plan: g<CR>
        with self._critical_section():
            # if not self.nvim.current.buffer['modifiable']: raise
            if range_[0] == range_[1]:
                range_ = (range_[0], range_[0] - 1)
            question = self._compose_question(args, range_, nocode=True)
            self._do_gpt_stop()
            self._do_gpt_open()
            if not args:
                self._do_gpt_multiline(question)
                return
            self._submit_question(question)

    @neovim.command('GPTCode', nargs='*', range=True)  # type: ignore
    def gpt_code(self, args, range_):  # plan: <CR> in visual
        with self._critical_section():
            question = self._compose_question(args, range_)
            self._do_gpt_stop()
            self._do_gpt_open()
            if not args:
                self._do_gpt_multiline(question)
                return
            self._submit_question(question)

    def _try_replace_template(self, arg):
        if arg.startswith('@'):
            key = arg[1:]
            if key in self._templates:
                return self._templates[key]
        return arg

    def _add_gpt_template(self, key, *args):
        keys = key.split(',')
        val = ' '.join(args)
        for key in keys:
            self._templates[key] = val

    @neovim.command('GPTTemplate', nargs='+')  # type: ignore
    def gpt_template(self, args):
        with self._critical_section():
            self._add_gpt_template(*args)

    def _join_args(self, args):
        return ' '.join(self._try_replace_template(a) for a in args)

    @neovim.command('GPTRegenerate', nargs='*', bang=True)  # type: ignore
    def gpt_regenerate(self, args, bang):  # plan: (r)egenerate
        additional_description = self._join_args(args)
        with self._critical_section():
            self._do_gpt_stop()
            if self._last_question is None:
                self.nvim.command('echo "No previous question asked"')
                return
            self._do_gpt_open()
            question = self._last_question
            if additional_description:
                question += '\n' + additional_description
            if bang:
                self._do_gpt_multiline(question, regenerate=True)
            else:
                self._submit_question(question, regenerate=True)

    def _submit_question(self, question, regenerate=False):
        if not len(question.strip()):
            return
        # if not regenerate:
        self._qa_count += 1
        #     qa_count = self._qa_count
        # else:
        #     qa_count = str(self._qa_count) + ' (Regenerated)'
        self._last_question = question
        question_ml = question.split('\n')
        question_ml = self._question_title.split('\n') + question_ml
        if regenerate:
            question_ml += self._regenerate_title.split('\n')
        question_ml += self._answer_title.split('\n')
        if len(self._cursors):
            self._cursor_counter = 0
            question_ml.append(self._cursors[self._cursor_counter])
        else:
            question_ml.append('')
        self._append_buffer(question_ml)
        bot = self.get_bot()
        if regenerate:
            bot.push_rewind()
        bot.push_question(question)
        self._transit_state('running')
        self._lock_cursor_to_end()

    @neovim.command('GPTAccept', bang=True)
    def gpt_accept(self, bang):  # plan: (a)ccept
        with self._critical_section():
            self._do_gpt_open()
            answer, full_answer = self._fetch_maybe_quoted_answer()
            if bang:
                answer = full_answer
            self._do_gpt_open(toggle=True)
            if self._last_bufnr is None or self._last_range is None:
                self.nvim.command('echo "no last range operation"')
                return
            try:
                buffer = self.nvim.buffers[self._last_bufnr]
            except neovim.NvimError:
                self.nvim.command('echo "buffer to edit ({}) is closed"'.format(self._last_bufnr))
                return
            if not buffer.options['modifiable']:
                self.nvim.command('echo "buffer not modifiable"')
                return
            buffer[self._last_range[0]-1:self._last_range[1]] = answer
            if answer:
                self._last_range = (self._last_range[0], self._last_range[0] + len(answer) - 1)
            else:
                self._last_bufnr = None
                self._last_range = None

    @neovim.command('GPTYank', bang=True)
    def gpt_yank(self, bang):
        with self._critical_section():
            self._do_gpt_open()
            answer, full_answer = self._fetch_maybe_quoted_answer()
            if bang:
                answer = full_answer
            answer = '\n'.join(answer)
            self.nvim.funcs.setreg('+', answer, 'l')
            self._do_gpt_open(toggle=True)

    @neovim.command('GPTExecute')
    def gpt_execute(self):  # plan: e(x)ecute
        answer, _ = self._fetch_maybe_quoted_answer()
        answer = '\n'.join(answer)
        # execute python expressions directly in rplugin process
        # exec(compile(answer, '<GPTExecute>', 'exec'))

    @neovim.command('GPTSync')
    def gpt_sync(self):
        with self._critical_section():
            bufnr = self.nvim.funcs.bufnr('GPT')
            if bufnr == -1:
                return
            if bufnr == self.nvim.funcs.bufnr('%'):
                self.nvim.command('buffer')
            bot = self.get_bot()
            full_answer = ''
            self._cursor_counter = (self._cursor_counter + 1) % len(self._cursors)
            while True:
                answer = bot.try_pop_answer()
                if answer is None:  # none means further queue pop would be blocking
                    break
                if self._stop_count:
                    print('dropped old answer:', answer)
                    if isinstance(answer, (Done, Shutdown)):
                        self._stop_count -= 1
                    continue
                if isinstance(answer, Done):  # done means end of a round of answer
                    self._append_last_line(full_answer)
                    self._rid_last_line_cursor()
                    self._transit_state('idle')
                    return
                if isinstance(answer, Shutdown):  # shutdown means worker thread crashed
                    full_answer += '\n**GPT WORKER CRASHED**:\n```\n'
                    full_answer += '\n'.join(LogSystem.instance().read_log().splitlines()[-6:])
                    full_answer += '\n```\nSee :GPTLog for more details.\n'
                    self._append_last_line(full_answer)
                    self._rid_last_line_cursor()
                    self._transit_state('idle')
                    return
                full_answer += answer
                # break  # remove this line
            self._append_last_line(full_answer)

    def _transit_state(self, state):
        if state == 'idle':
            assert self._state == 'running'
            self.nvim.command('lua if _gpt_sync_timer then _gpt_sync_timer:stop() end')
        elif state == 'running':
            assert self._state == 'idle'
            self.nvim.command('lua _gpt_sync_timer = vim.loop.new_timer()')
            self.nvim.command('lua _gpt_sync_timer:start({interval}, {interval}, vim.schedule_wrap(function () vim.cmd [[GPTSync]] end))'.format(interval=self._update_interval))
        self._state = state

    def _append_last_line(self, content):
        if not len(content):
            if len(self._cursors):
                with self._modifiable_buffer() as buffer:
                    # Just worth it to make it so fxxking sense of technology!!!!
                    last_line = buffer[-1]
                    if len(last_line) and last_line[-1] in self._cursors:
                        last_line = last_line[:-1]
                    buffer[-1] = last_line + self._cursors[self._cursor_counter]
            return
        lines = content.split('\n')
        if not len(lines):
            return
        with self._modifiable_buffer() as buffer:
            last_line = buffer[-1]
            if len(self._cursors):
                lines[-1] = lines[-1] + self._cursors[self._cursor_counter]
            if len(self._cursors):
                if len(last_line) and last_line[-1] in self._cursors:
                    last_line = last_line[:-1]
                buffer[-1] = last_line + lines[0]
            else:
                buffer[-1] = last_line + lines[0]
            if len(lines) > 1:
                buffer.append(lines[1:])
        self._lock_cursor_to_end()

    def _lock_cursor_to_end(self):
        if self.nvim.funcs.bufnr('%') != self.nvim.funcs.bufnr('GPT'):
            return
        if self._lock_last_line != 'force':
            if self._lock_last_line in ('last-char', 'last-line'):
                buffer = self._get_buffer()
                if len(buffer) > self.nvim.funcs.getcurpos()[1]:
                    return
                if self._lock_last_line == 'last-char':
                    if len(buffer[-1]) > self.nvim.funcs.getcurpos()[2] + 4:
                        return
        self.nvim.command('norm! G$')

    def _rid_last_line_cursor(self):
        if not len(self._cursors):
            return
        with self._modifiable_buffer() as buffer:
            last_line = buffer[-1]
            if len(last_line) and last_line[-1] in self._cursors:
                buffer[-1] = last_line[:-1]

    def _append_buffer(self, lines):
        with self._modifiable_buffer() as buffer:
            buffer.append(lines)

    def _set_buffer(self, lines):
        with self._modifiable_buffer() as buffer:
            buffer[:] = lines

    def _get_buffer(self):
        bufnr = self.nvim.funcs.bufnr("GPT")
        if bufnr == -1:
            raise RuntimeError('GPT window not open, please :GPTOpen first')
        return self.nvim.buffers[bufnr]

    @contextlib.contextmanager
    def _modifiable_buffer(self, buffer=None):
        if buffer is None:
            buffer = self._get_buffer()
        buffer.options['modifiable'] = True
        try:
            yield buffer
        finally:
            buffer.options['modifiable'] = False

    def _fetch_maybe_quoted_answer(self):
        buffer = self._get_buffer()
        in_quotes = False
        has_quotes = False
        in_answer = True
        has_colon = False
        full_answer = []
        quoted_answer = []
        coloned_answer = []
        question_title_prefix = self._question_title.strip()
        answer_title_prefix = self._answer_title.strip()
        for i in range(len(buffer)):
            line = buffer[i]
            if line.startswith('```'):
                in_quotes = not in_quotes
                has_quotes = True
                continue
            if line.startswith(question_title_prefix):
                in_answer = False
                continue
            if line.startswith(answer_title_prefix):
                has_quotes = False
                in_answer = True
                has_colon = False
                full_answer.clear()
                quoted_answer.clear()
                coloned_answer.clear()
                continue
            if not in_quotes:
                if line.endswith(':'):
                    has_colon = True
            if in_answer:
                if in_quotes:
                    quoted_answer.append(line)
                if has_colon:  # todo: test colon with true data
                    coloned_answer.append(line)
                full_answer.append(line)
        answer = quoted_answer if has_quotes else (coloned_answer if has_colon else full_answer)
        # while answer and not answer[-1]:
        #     answer.pop()  # rid trailing empty lines
        return answer, full_answer

    def _determine_range_filetype(self, range_):
        buffer = self.nvim.current.buffer
        filetype = buffer.options['filetype']
        if filetype == 'markdown':
            ft = None
            for i in range(1, min(len(buffer) + 1, range_[0])):
                line = buffer[i - 1]
                if line.startswith('```'):
                    if ft is None:
                        ft = line[3:]
                    else:
                        ft = None
            if ft is not None:
                filetype = ft
        if filetype is None:
            filetype = ''
        return filetype

    def _compose_question(self, args, range_=None, nocode=False):
        question = self._join_args(args)
        curr_bufnr = self.nvim.funcs.bufnr('%')
        if range_ and curr_bufnr != self.nvim.funcs.bufnr('GPT'):
            self._last_bufnr = curr_bufnr
            self._last_range = tuple(range_)
        if range_ is not None:
            buffer_section = self.nvim.current.buffer[range_[0]-1:range_[1]]
            code = '\n'.join(buffer_section) if not nocode else ''
            if '{filetype}' in self._code_quote or '{filetype}' in self._in_language:
                filetype = self._determine_range_filetype(range_)
            else:
                filetype = ''
            if not len(code.strip()):

                if filetype:
                    question = self._in_language.format(question=question, filetype=filetype)
            else:
                question = self._code_quote.format(question=question, code=code, filetype=filetype)
        return question #.strip()

    def _set_welcome_message(self):
        # from .workers import model_worker_type
        bot_name = self._model # model_worker_type(self._model)
        if len(self._welcome_messages) == 1:
            self._set_buffer([self._welcome_messages[0].format(bot_name)])
        elif len(self._welcome_messages) > 2:
            import random
            self._set_buffer([random.choice(self._welcome_messages).format(bot_name)])
        else:
            self._set_buffer([])
        self._lock_cursor_to_end()

    @contextlib.contextmanager
    def _critical_section(self):
        if not self._mutex.acquire(timeout=2.5):
            raise RuntimeError('mutex acquire failed, last entry: {}'.format(self._last_entry_func))
        self._last_entry_func = inspect.stack()[2].function
        try:
            yield
        finally:
            self._last_entry_func = None
            self._mutex.release()


__all__ = ['GPTPlugin']
