local M = {}

function M.add_suggested_keymaps()
    local _gpt_add_key_map_timer = vim.loop.new_timer()
    _gpt_add_key_map_timer:start(100, 100, vim.schedule_wrap(function ()
        if _gpt_add_key_map_timer and pcall(function () vim.cmd [[GPTSuggestedKeymaps]] end) then
            _gpt_add_key_map_timer:stop()
            _gpt_add_key_map_timer = nil
        end
    end))
end

function M.setup()
end

return M
