-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

local Paths = require 'Paths'
local M = {}
M.defaults = { pathMode = 'hierarchy', pathPrefix = '', pathSuffix = '',
    stripLeading = 0, stripTrailing = 0, maxDepth = 0 }
local function parts(value)
    local result = {}
    for part in value:gmatch('[^/]+') do result[#result + 1] = part end
    return result
end
local function folder(value)
    assert(type(value) == 'string', LOC("$$$/FolderTreePublisher/SubfolderString=The subfolder must be text."))
    value = value:gsub('\\', '/')
    if value == '' then return value end
    Paths.relativeFile(value)
    for _, part in ipairs(parts(value)) do
        assert(not part:find('[<>"|?*%c]') and not part:match('[ .]$'), LOC("$$$/FolderTreePublisher/InvalidSubfolder=Invalid subfolder name: ") .. part)
        local stem = (part:match('^[^.]+') or ''):upper()
        assert(stem ~= 'CON' and stem ~= 'PRN' and stem ~= 'AUX' and stem ~= 'NUL'
            and not stem:match('^COM[1-9]$') and not stem:match('^LPT[1-9]$'), LOC("$$$/FolderTreePublisher/ReservedSubfolder=Reserved subfolder name: ") .. part)
    end
    return value
end
function M.settings(input)
    local s = {}
    for key, default in pairs(M.defaults) do
        local value = input and input[key]
        if value == nil then value = default end
        s[key] = value
    end
    assert(s.pathMode == 'hierarchy' or s.pathMode == 'flat', LOC("$$$/FolderTreePublisher/UnknownPathMode=Unknown path mode."))
    s.pathPrefix, s.pathSuffix = folder(s.pathPrefix), folder(s.pathSuffix)
    for _, key in ipairs { 'stripLeading', 'stripTrailing', 'maxDepth' } do
        local n = tonumber(s[key])
        assert(n and n >= 0 and n <= 100 and n == math.floor(n), LOC("$$$/FolderTreePublisher/InvalidDepth=The number of levels must be an integer from 0 to 100."))
        s[key] = n
    end
    return s
end
function M.apply(relative, input)
    local s = M.settings(input)
    local components = parts(Paths.relativeFile(relative))
    local filename = table.remove(components)
    local folders = {}
    if s.pathMode == 'hierarchy' then
        for i = s.stripLeading + 1, #components - s.stripTrailing do
            if s.maxDepth == 0 or #folders < s.maxDepth then folders[#folders + 1] = components[i] end
        end
    end
    local output = {}
    if s.pathPrefix ~= '' then output[#output + 1] = s.pathPrefix end
    if #folders > 0 then output[#output + 1] = table.concat(folders, '/') end
    if s.pathSuffix ~= '' then output[#output + 1] = s.pathSuffix end
    output[#output + 1] = filename
    return Paths.relativeFile(table.concat(output, '/'))
end
function M.view(f, publishSettings, info)
    local View = import 'LrView'
    local s, transient = info.collectionSettings, info.pluginContext
    for key, default in pairs(M.defaults) do if s[key] == nil then s[key] = default end end
    local example = LOC("$$$/FolderTreePublisher/ExamplePath=Photos/2026/Trip/IMG_001.jpg")
    local function update()
        local ok, path = pcall(M.apply, example, s)
        s.LR_canSaveCollection = ok
        transient.hierarchyEnabled = s.pathMode == 'hierarchy'
        transient.preview = ok and ((publishSettings.destinationRoot or '') .. '/' .. path) or tostring(path)
    end
    for key in pairs(M.defaults) do s:addObserver(key, update) end
    update()
    local function row(label, control)
        return f:row { f:static_text { title = label, width = 230 }, control }
    end
    local function number(key)
        return f:edit_field { value = View.bind(key), precision = 0, min = 0, max = 100,
            width_in_chars = 6, enabled = View.bind { key = 'hierarchyEnabled', bind_to_object = transient } }
    end
    return f:group_box {
        title = LOC("$$$/FolderTreePublisher/CollectionPath=Publication path for this collection"), bind_to_object = s,
        spacing = f:control_spacing(),
        row(LOC("$$$/FolderTreePublisher/Mode=Mode"), f:popup_menu { value = View.bind('pathMode'), items = {
            { title = LOC("$$$/FolderTreePublisher/KeepHierarchy=Keep folder hierarchy"), value = 'hierarchy' },
            { title = LOC("$$$/FolderTreePublisher/Flat=Put everything in one folder"), value = 'flat' },
        }}),
        row(LOC("$$$/FolderTreePublisher/Prefix=Subfolder before hierarchy"), f:edit_field { value = View.bind('pathPrefix'), width_in_chars = 32 }),
        row(LOC("$$$/FolderTreePublisher/StripLeading=Remove levels from the start"), number('stripLeading')),
        row(LOC("$$$/FolderTreePublisher/StripTrailing=Remove levels from the end"), number('stripTrailing')),
        row(LOC("$$$/FolderTreePublisher/MaxDepth=Keep first levels (0 = all)"), number('maxDepth')),
        row(LOC("$$$/FolderTreePublisher/Suffix=Subfolder after hierarchy"), f:edit_field { value = View.bind('pathSuffix'), width_in_chars = 32 }),
        f:static_text { title = LOC("$$$/FolderTreePublisher/PathHelp=Subfolders are relative to the publication folder, e.g. Clients/Anna.^nOrder: trim start -> trim end -> limit depth -> add subfolders."),
            width_in_chars = 80, height_in_lines = 2 },
        f:static_text { title = LOC("$$$/FolderTreePublisher/ExampleLabel=Example source path: ") .. example },
        f:static_text { title = View.bind { key = 'preview', bind_to_object = transient },
            width_in_chars = 80, height_in_lines = 3 },
        f:static_text { title = LOC("$$$/FolderTreePublisher/RepublishHelp=After changing the path, click Publish. Existing publications will be marked^nfor update. Filenames and export settings stay the same."),
            width_in_chars = 80, height_in_lines = 2 },
    }
end
return M
