suggested_keymaps = '''
" <CR> input, g<CR> line, gs<CR> word, gu<CR> file
nnoremap {trigger} :GPTInput<Space>
vnoremap {trigger} :GPTCode<Space>
nnoremap <silent> g{trigger} <Cmd>.GPTCode<CR>
" nnoremap <silent> g{trigger} <Cmd>exec ":GPTInput " . getline('.')<CR>
nnoremap <silent> gs{trigger} <Cmd>exec ":GPTInput " . expand('<cword>')<CR>
nnoremap <silent> gu{trigger} <Cmd>%GPTCode<CR>
'''

gpt_window_keymaps = '''
" (i)nput (a)ccept (r)egenerate (d)iscard e(x)ecute (s)top (q)uit
nnoremap <buffer> i :GPTInput<Space>
nnoremap <buffer><silent> a <Cmd>GPTAccept<CR>
nnoremap <buffer><silent> r <Cmd>GPTRegenerate<CR>
nnoremap <buffer><silent> d <Cmd>GPTDiscard<CR>
nnoremap <buffer><silent> x <Cmd>GPTExecute<CR>
nnoremap <buffer><silent> s <Cmd>GPTStop<CR>
nnoremap <buffer><silent> q <Cmd>wincmd q<CR>
nnoremap <buffer><silent> <Esc> <Cmd>wincmd q<CR>
'''

suggested_templates = '''
GPTTemplate p,plain Note that you shall only output the answer, with no additional text like 'Sure' or 'Here is the result'.
GPTTemplate q,quote Please wrap the answer with triple quotes like ```answer```.
GPTTemplate c,cont Please continue.
GPTTemplate a,again The answer is wrong, please try again.
GPTTemplate g,guess Guess the purpose of this code. Explain it step-by-step.
GPTTemplate t,test Write a test for this code.
GPTTemplate d,document Write an documentation or API reference for this code.
GPTTemplate b,bench Write a benchmark for this code. You may want to use the Google Benchmark as framework.
GPTTemplate s,simplify Rewrite to simplify this.
GPTTemplate n,naming Rename the variable and function names to make them more readable.
GPTTemplate r,readable Rewrite to make this code more readable and maintainable.
GPTTemplate o,optimize How to optimize this code to make it faster?
GPTTemplate e,extract Extract the computation of some variables to separate functions for maintainable code.
GPTTemplate m,mdlink Here is a markdown file that have several links in the format [name](link), please fill the links according to given name. You may want to search the web if you are not sure about the link.
GPTTemplate l,longer Make this expression longer and fullfilling.
GPTTemplate a,abstract Summerize these text in as less sentences as possible.
GPTTemplate w,web You may want to search the web.
'''

__all__ = ['suggested_keymaps', 'gpt_window_keymaps', 'suggested_templates']
