# nvim-gpt

Integrated **ChatGPT** and **Bing AI** in NeoVim just for neo-pioneers like you :)

## Usage

In normal mode:

- Press `<CR>` or `:GPT <question>` to enter GPT prompt, input your question, and you get the answer in the pop-up GPT window on the right.
- Press `g<CR>` or `:GPTWrite <question>` to enter GPT prompt, input your requiement description for code (e.g. write a quick sort). The current filetype will be automatically appended for you (e.g. write a quick sort, in cpp), and you get the code in the pop-up GPT window. And after GPT completes their answer you may press 'a' to insert the code directly to where you pressed `g<CR>`.

In visual mode:

- Press `<CR>` or `:GPTCode <question>` to enter GPT prompt, input the question you want to ask or action you want to do on the code. The code will be appended to the question, and you will get the output code from GPT in the pop-up GPT window.

Utilize the cool vim range expressions:

- Try `:%GPTCode` for sending the whole file to GPT.
- Try `:.GPTCode` for sending only the current line to GPT.
- Try `:1,.GPTCode` for sending from first line to current line to GPT.
- Try `:.,$GPTCode` for sending from current line to last line to GPT.
- Try `:-5,+4GPTCode` for sending from the previous 5 lines and the next 4 lines to GPT.
- Try `:'<,'>GPTCode` for sending the selected (visual mode) lines to GPT.

In the GPT prompt:

- You may type 'How to fix this error?' to describe the task for GPT.
- But we've already got some nice templates for you, to use the template named 'fix' for example, simply type: `@f` or `@fix`, it will be automatically replaced by `How to fix this error?`
- There is also a useful template called `@q` or `@quote` which is equivalent to `Please wrap the final answer with triple quotes`, which not only gives us a better syntax highlighting for code, but also make it easier to seperate the real answer from GPT's descriptive text like `Sure` or `Here is the result:`, see below.
- See [keymaps.py](rplugin/python3/py_nvim_gpt/keymaps.py) for a complete list of all templates provided by default, you may override the templates in the setup option `question_templates = ...`, see bottom.
- If you want to edit multi-line questions, simply press `<Esc>` then `i` to enter insert mode again. Now pressing `<CR>` in insert mode won't trigger submit anymore, and you may use `<CR>` or `o` in normal mode to compose multi-line questions. After finished editing the question, press `<CR>` in normal mode to submit. The question buffer is remained when you use `r` to regenerate answer from GPT.

In the GPT window:

- Suppose you just got the code generated by GPT in the GPT window, now press `a` to accept their change, and apply it to your previous visual selected code lines (simply replace it).
- Pressing `a` will only paste the code into your file, excluding the descriptive texts, when a triple-quoted \`\`\` code block is found.
- If you dislike the current answer, you may press `r` to re-edit the question (if needed), then press `<CR>` again let GPT to regenerate a different solution.
- Press `d` to delete all memory of this GPT session, i.e. reset.
- Press `s` to stop GPT from generating the complete answer.
- Press `q` or `<Esc>` to close the GPT window and back to where you're editing.
- Press `i` to follow up with a new question (equivalent to `:GPT`).

## Multi-backend support

You may use `:GPTModel <model_name>` to switch to another model, e.g. `:GPTModel creative` to switch to the Bing AI - 'creative'. The default model is 'gpt-3.5-turbo', which can be tweaked in setup options, see below.

If you have [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim), use `:Telescope gpt_models` to show a list of all GPT models to select from.

## Install

It's suggested to use [packer.nvim](https://github.com/wbthomason/packer.nvim) to manage NeoVim plugins, this plugin for example:

```lua
use({
    'archibate/nvim-gpt',
    -- optional for supporting ':Telescope gpt_models' and ':Telescope gpt_inputs' commands (TBD)
    requires = { 'nvim-telescope/telescope.nvim' },
    config = function()
        require'nvim-gpt'.setup {
            model = 'gpt-3.5-turbo',
            window_width = 45,
            -- see more setup options in section 'Setup options' below
        }
    end,
})
```

After adding above code to `init.lua`, restart nvim and run `:PackerInstall` and `:PackerCompile`.

Then try run `:GPTOpen` command and if everything working fine the GPT window should shows up.

> If not, try `:UpdateRemotePlugins`.

### For ChatGPT users

[openai-python](https://github.com/openai/openai-python) is required for using the ChatGPT backend.

```bash
pip install openai
```

1. Obtain an API key from OpenAI: https://beta.openai.com

2. Add this to your `~/.bashrc`:

```bash
export OPENAI_API_KEY=sk-**********  # replace this with your API key
```

3. and then restart your shell, enter nvim and choose `gpt-3.5-turbo` as model, which is default.

### For Bing AI users

[EdgeGPT](https://github.com/acheong08/EdgeGPT) is required for using the Bing AI backend.

```bash
pip install EdgeGPT
```

1. Obtain the cookies JSON via [Cookie Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi) plugin from the [Bing site](https://bing.com/chat).

2. Paste the cookies into file `~/.bing-cookies.json`.

3. Enter nvim and `:GPTModel balanced`. For setting Bing AI as default, add `model = 'balanced'` to setup options.

### For Google users

[googlesearch-python](https://pypi.org/project/googlesearch-python) is required for using the Google search backend.

```bash
pip install googlesearch-python
```

Then enter nvim and `:GPTModel googlesearch-python`. Now search current word with `gy<CR>`, current line with `gs<CR>`.

## Keymaps

There are keymaps applied **by default** when loading this plugin. See [keymaps.py](rplugin/python3/py_nvim_gpt/keymaps.py):

```vim
" <CR> input, g<CR> line, gs<CR> word, gu<CR> file
nnoremap <CR> :GPT<Space>
vnoremap <CR> :GPTCode<Space>
nnoremap g<CR> :GPTWrite<Space>
nnoremap <silent> gs<CR> <Cmd>exec ":GPT " . getline('.')<CR>
nnoremap <silent> gy<CR> <Cmd>exec ":GPT " . expand('<cword>')<CR>
nnoremap <silent> gu<CR> <Cmd>%GPTCode<CR>
```

Can be disabled by `no_default_keymaps = true` option in setup.

### GPT window keymaps

Apart from universal keymaps above, inside the GPT window, which is not modifiable, also have their own keymaps:

```vim
" (i)nput (a)ccept (r)egenerate (d)iscard e(x)ecute (s)top (q)uit
nnoremap <buffer><silent> i <Cmd>GPT<CR>
nnoremap <buffer><silent> a <Cmd>GPTAccept<CR>
nnoremap <buffer><silent> A <Cmd>GPTAccept!<CR>
nnoremap <buffer><silent> r <Cmd>GPTRegenerate!<CR>
nnoremap <buffer><silent> dd <Cmd>GPTDiscard<CR>
nnoremap <buffer><silent> x <Cmd>GPTExecute<CR>
nnoremap <buffer><silent> s <Cmd>GPTStop<CR>
nnoremap <buffer><silent> q <Cmd>wincmd q<CR>
nnoremap <buffer><silent> <Esc> <Cmd>wincmd q<CR>
```

### GPT multiline edit keymaps

```vim
nnoremap <buffer><silent> <CR> <Cmd>GPTMultiline<CR>
inoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
snoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
inoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
snoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
nnoremap <buffer><silent> q <Cmd>wincmd q<CR>
nnoremap <buffer><silent> <Esc> <Cmd>wincmd q<CR>
autocmd BufLeave <buffer={bufnr}> exec bufwinnr({bufnr}) == -1 ? "" : bufwinnr({bufnr}) . "wincmd q"
```

## All setup options

```lua
require'nvim-gpt'.setup {
    -- which backend to use: gpt-3.5-turbo, creative, balanced, percise, google-search
    model = 'gpt-3.5-turbo',
    -- may provide specific parameters like temperature depends on models
    params = {
        ['gpt-3.5-turbo'] = {
            -- see https://platform.openai.com/docs/api-reference/chat/create
            temperature = 0.85,
            top_p = 1,
            n = 1,
            presence_penalty = 0,
            frequency_penalty = 0,
        },
        ['google-search'] = {
            -- see https://pypi.org/project/googlesearch-python
            num_results = 10,
            sleep_interval = 0,
            timeout = 5,
            lang = 'en',
            format = '# {title}\n{url}\n\n{desc}',
        },
    },
    -- '|/_\\' = rotating loading symbol, '_ ' = blinking on and off, '' = disable
    cursors = '|/_\\',
    -- this is how we quote code when :'<,'>GPTCode
    code_quote = '{question}\n```{filetype}\n{code}\n```',
    -- this is how we quote language type when :GPTWrite
    in_language = '{question}\n(in {filetype})',
    -- title indicating human question in GPT window
    question_title = '\n🙂:',
    -- title indicating bot answer in GPT window
    answer_title = '\n🤖:',
    -- marker use when human requests to regenerate
    regenerate_title = '🔄',
    -- whether to show bot's welcome messages on start up: 'fancy', '🤖 {}', 'none'
    welcome_messages = '🤖 {}',
    -- GPT window width
    window_width = 45,
    -- GPT window specific options
    window_options = {
        wrap = true,
        list = false,
        cursorline = true,
        number = false,
        relativenumber = false,
    },
    -- whether we lock to last line when answer: none, last-char, last-line, force
    lock_last_line = 'force',
    -- GPT window update interval (ms) when streaming the answer
    update_interval = 180,
    -- automatically add default keymaps (see 'Keymaps' section below)
    no_default_keymaps = false,
    -- preset templates, can be used like @p or @plain in :GPT or :GPTCode
    question_templates = [[
GPTTemplate p,plain Note that you shall only output the plain answer, with no additional text like 'Sure' or 'Here is the result'.
GPTTemplate q,quote Please wrap the final answer with triple quotes like ```answer```.
GPTTemplate a,again The answer is wrong, please try again.
GPTTemplate t,test Write a test for this code.
GPTTemplate d,document Write an documentation or API reference for this code.
GPTTemplate b,bugs Could you find any possible bugs in this code?
GPTTemplate gb,googlebench Write a benchmark for this code. You may want to use the Google Benchmark as framework.
GPTTemplate s,simplify Rewrite to simplify this.
GPTTemplate ed,editfix Edit the code to fix the problem.
GPTTemplate f,fix How to fix this error?
GPTTemplate ex,explain Explain the purpose of this code, step by step.
GPTTemplate n,naming Rename the variable and function names to make them more readable.
GPTTemplate r,readable Rewrite to make this code more readable and maintainable.
GPTTemplate sp,split This line is too long and complex. Could you split it for readability?
GPTTemplate du,duplicate Please reduce duplication by following the Don't Repeat Yourself principle.
GPTTemplate c,complete Complete the missing part of code with given context.
GPTTemplate i,implement Implement the function based on its calling signature.
GPTTemplate li,linkmd Here is a markdown file that have several links in the format [name](link), please fill the links according to given name. You may want to search the web if you are not sure about the link.
GPTTemplate l,longer Make this expression longer and fullfilling.
GPTTemplate t,think Let's think step by step.
GPTTemplate v,verify Could you verify this?
GPTTemplate w,web You may want to search the web.
GPTTemplate o,omit Since the output length is limited. Please omit the unchanged part with ellipses. Only output the changed or newly-added part.
GPTTemplate m,multiple Please provide multiple different versions of answer for reference.
GPTTemplate g,grammar Fix possible grammar issues or typos in my writing.
GPTTemplate wo,wording Rewrite with better choices of words.
GPTTemplate tr,translate Translate from Chinese to English, or from English to Chinese.
    ]],
}
```

Found bugs or any suggestions? Please let me know by opening a [GitHub issue](https://github.com/archibate/nvim-gpt/issues/new), I'm glad to help.
