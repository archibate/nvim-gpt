local M = {}

local function add_default_keymaps()
    vim.cmd [[
nnoremap <silent> <CR> <Cmd>GPT<CR>
vnoremap <silent> <CR> <Cmd>GPTCode<CR>
nnoremap <silent> g<CR> <Cmd>GPTWrite<CR>
nnoremap <silent> @<CR> <Cmd>Telescope nvim-gpt gpt_template initial_mode=insert<CR>
nnoremap <silent> g@<CR> <Cmd>Telescope nvim-gpt gpt_history<CR>
vnoremap <silent> @<CR> <Cmd>GPTCode<CR><Cmd>Telescope nvim-gpt gpt_template initial_mode=insert<CR>
vnoremap <silent> g@<CR> <Cmd>GPTCode<CR><Cmd>Telescope nvim-gpt gpt_history<CR>
nnoremap <silent> gs<CR> <Cmd>exec ":GPT " . getline('.')<CR>
nnoremap <silent> gy<CR> <Cmd>exec ":GPT " . expand('<cword>')<CR>
nnoremap <silent> gu<CR> <Cmd>%GPTCode<CR>
nnoremap <silent> gsm<CR> <Cmd>Telescope nvim-gpt gpt_model<CR>
" to prevent this mapping interfere with quickfix selection:
" autocmd CmdwinEnter * nnoremap <CR> <CR>
" autocmd BufReadPost quickfix nnoremap <CR> <CR>
]]
end

function M.setup(opts)
    if not opts.no_default_keymaps then
        add_default_keymaps()
    end
    M._setup_options = opts
end

function M.get_model_list()
    return vim.api.nvim_call_function('GPTModelList', {}) or vim.api.nvim_call_function('GPTModelList', {}) or {'none', {'none'}}
end

function M.get_prompt_history()
    return vim.api.nvim_call_function('GPTPromptHistory', {}) or vim.api.nvim_call_function('GPTPromptHistory', {}) or {}
end

function M.get_template_list()
    return vim.api.nvim_call_function('GPTTemplateList', {}) or vim.api.nvim_call_function('GPTTemplateList', {}) or {}
end

return M
