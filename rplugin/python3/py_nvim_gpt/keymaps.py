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
'''

gpt_multiline_edit_keymaps = '''
nnoremap <buffer><silent> <CR> <Cmd>GPTMultiline<CR>
inoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
snoremap <expr><buffer><silent> <CR> (!exists('b:_no_enter_submit') ? '<Esc><Cmd>GPTMultiline<CR>' : '<CR>')
inoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
snoremap <buffer><silent> <Esc> <Esc><Cmd>let b:_no_enter_submit = 1<CR>
nnoremap <buffer><silent> q <Cmd>wincmd q<CR>
nnoremap <buffer><silent> <Esc> <Cmd>wincmd q<CR>
autocmd BufLeave <buffer={bufnr}> exec bufwinnr({bufnr}) == -1 ? "" : bufwinnr({bufnr}) . "wincmd q"
'''

preset_templates = '''
GPTTemplate p,plain Note that you shall only output the plain answer, with no additional text like 'Sure' or 'Here is the result'.
GPTTemplate q,quote Please wrap the final answer with triple quotes like ```answer```.
GPTTemplate a,again The answer is wrong, please try again.
GPTTemplate t,test Write a test for this code.
GPTTemplate d,document Write an documentation or API reference for this code.
GPTTemplate b,bugs Could you find any possible BUGs in this code?
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
GPTTemplate tr,translate Translate from Chinese to English, or English to Chinese.
'''
