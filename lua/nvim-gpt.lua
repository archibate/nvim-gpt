local M = {}

local function add_default_keymaps()
    vim.cmd [[
" <CR> input, g<CR> line, gs<CR> word, gu<CR> file
nnoremap <CR> :GPT<Space>
vnoremap <CR> :GPTCode<Space>
nnoremap g<CR> :GPTWrite<Space>
nnoremap <silent> gs<CR> <Cmd>exec ":GPT " . getline('.')<CR>
nnoremap <silent> gy<CR> <Cmd>exec ":GPT " . expand('<cword>')<CR>
nnoremap <silent> gu<CR> <Cmd>%GPTCode<CR>
" to prevent this mapping interfere with quickfix selection:
autocmd CmdwinEnter * nnoremap <CR> <CR>
autocmd BufReadPost quickfix nnoremap <CR> <CR>
]]
end

function M.setup(opts)
    if not opts.no_default_keymaps then
        add_default_keymaps()
    end
    M._setup_options = opts
end

return M
