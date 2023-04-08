local pickers = require "telescope.pickers"
local finders = require "telescope.finders"
local conf = require("telescope.config").values
local actions = require "telescope.actions"
local action_state = require "telescope.actions.state"
local nvim_gpt = require'nvim-gpt'

return require'telescope'.register_extension {
    setup = function(ext_config, config)
        local _ = {ext_config, config}
    end,
    exports = {
        gpt_model = function(opts)
            opts = opts or {}
            local gpt_models = nvim_gpt.get_model_list()
            local curr_model = gpt_models[1]
            gpt_models = gpt_models[2]
            pickers.new(opts, {
                prompt_title = "GPTModel",
                finder = finders.new_table {
                    results = gpt_models,
                },
                sorter = conf.generic_sorter(opts),
                attach_mappings = function(prompt_bufnr, map)
                    actions.select_default:replace(function()
                        actions.close(prompt_bufnr)
                        local selection = action_state.get_selected_entry()
                        vim.cmd("GPTModel " .. selection[1])
                    end)
                    return true
                end,
            }):find()
        end,
        gpt_history = function(opts)
            opts = opts or {}
            local questions = nvim_gpt.get_prompt_history()
            pickers.new(opts, {
                prompt_title = "GPTHistory",
                finder = finders.new_table {
                    results = questions,
                },
                sorter = conf.generic_sorter(opts),
                attach_mappings = function(prompt_bufnr, map)
                    actions.select_default:replace(function()
                        actions.close(prompt_bufnr)
                        local selection = action_state.get_selected_entry()
                        vim.cmd("GPT")
                        vim.api.nvim_put({ selection[1] }, "", false, true)
                    end)
                    return true
                end,
            }):find()
        end,
        gpt_template = function(opts)
            opts = opts or {}
            local templates = nvim_gpt.get_template_list()
            pickers.new(opts, {
                prompt_title = "GPTTemplate",
                finder = finders.new_table {
                    results = templates,
                },
                sorter = conf.generic_sorter(opts),
                attach_mappings = function(prompt_bufnr, map)
                    actions.select_default:replace(function()
                        actions.close(prompt_bufnr)
                        local selection = action_state.get_selected_entry()
                        vim.cmd("GPT!")
                        vim.api.nvim_put({ selection[1] }, "", true, true)
                    end)
                    return true
                end,
            }):find()
        end,
    },
}
