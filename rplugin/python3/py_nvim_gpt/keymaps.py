gpt_window_keymaps = '''
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
autocmd BufHidden,BufDelete <buffer> exec bufwinnr("GPTInput") == -1 ? "" : bufwinnr("GPTInput") . "wincmd q"
'''

gpt_multiline_edit_keymaps = '''
nnoremap <buffer><silent> <CR> <Cmd>GPTMultiline<CR>
vnoremap <buffer><silent> <CR> <Cmd><C-u>GPTMultiline<CR>
inoremap <buffer><silent> @<CR> <Cmd>Telescope nvim-gpt gpt_template initial_mode=insert<CR>
inoremap <buffer><silent> g<CR> <Cmd>Telescope nvim-gpt gpt_history<CR>
snoremap <buffer><silent> @<CR> <Cmd>Telescope nvim-gpt gpt_template initial_mode=insert<CR>
snoremap <buffer><silent> g<CR> <Cmd>Telescope nvim-gpt gpt_history<CR>
inoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
snoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
inoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
snoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
nnoremap <buffer><silent> q <Cmd>wincmd q<CR>
nnoremap <buffer><silent> <Esc> <Cmd>wincmd q<CR>
'''

preset_templates = '''
Note that you shall only output the plain answer, with no additional text like 'Sure' or 'Here is the result'.
Please wrap the final answer with triple quotes like ```answer```.
The answer is wrong, please try again.
Write a test for this code.
Write an documentation or API reference for this code.
Could you find any possible BUGs in this code?
Write a benchmark for this code. You may want to use the Google Benchmark as framework.
Rewrite to simplify this.
Edit the code to fix the problem.
How to fix this error?
Explain the purpose of this code, step by step.
Rename the variable and function names to make them more readable.
Rewrite to make this code more readable and maintainable.
This line is too long and complex. Could you split it for readability?
Please reduce duplication by following the Don't Repeat Yourself principle.
Complete the missing part of code with given context.
Implement the function based on its calling signature.
Here is a markdown file that have several links in the format [name](link), please fill the links according to given name. You may want to search the web if you are not sure about the link.
Make this expression longer and fullfilling.
Let's think step by step.
Could you verify this?
You may want to search the web.
Since the output length is limited. Please omit the unchanged part with ellipses. Only output the changed or newly-added part.
Please provide multiple different versions of answer for reference.
Fix possible grammar issues or typos in my writing.
Rewrite with better choices of words.
Translate from Chinese to English, or English to Chinese.
'''
