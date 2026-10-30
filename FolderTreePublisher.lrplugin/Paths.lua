-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

-- Pure Lua path validation; separators are converted back by LrPathUtils at the boundary.
local M = {}
function M.normalize(path)
    assert(type(path) == 'string' and path ~= '', LOC("$$$/FolderTreePublisher/MissingPath=No path specified."))
    assert(not path:find('%z'), LOC("$$$/FolderTreePublisher/InvalidPath=Invalid path."))
    local p = path:gsub('\\', '/')
    assert(p:sub(1, 1) == '/' or p:match('^%a:/'), LOC("$$$/FolderTreePublisher/AbsolutePath=An absolute path is required."))
    for part in p:gmatch('[^/]+') do
        assert(part ~= '.' and part ~= '..', LOC("$$$/FolderTreePublisher/DotPath=The path must not contain . or .."))
    end
    local unc = p:sub(1, 2) == '//'
    p = p:gsub('/+', '/')
    if unc then p = '/' .. p end
    p = p:gsub('/+$', '')
    if p == '' then return '/' end
    if p:match('^%a:$') then return p .. '/' end
    return p
end
local function key(p)
    p = M.normalize(p)
    if p:match('^%a:/') or p:sub(1, 2) == '//' then return p:lower() end
    return p
end
function M.relative(root, path)
    root, path = M.normalize(root), M.normalize(path)
    if key(root) == key(path) then return '' end
    local prefix = root:sub(-1) == '/' and root or root .. '/'
    assert(key(path:sub(1, #prefix)) == key(prefix), LOC("$$$/FolderTreePublisher/OutsideRoot=File is outside the source root: ") .. path)
    return path:sub(#prefix + 1)
end
function M.validateRoots(source, destination)
    source, destination = M.normalize(source), M.normalize(destination)
    local a = pcall(M.relative, source, destination)
    local b = pcall(M.relative, destination, source)
    assert(not a and not b, LOC("$$$/FolderTreePublisher/OverlappingRoots=The source and publication folders must not overlap or contain each other."))
    return source, destination
end
function M.relativeFile(path)
    assert(type(path) == 'string' and path ~= '' and not path:find('[\\:%z]') and path:sub(1,1) ~= '/', LOC("$$$/FolderTreePublisher/InvalidRelative=Invalid relative path."))
    for part in path:gmatch('[^/]+') do
        assert(part ~= '.' and part ~= '..', LOC("$$$/FolderTreePublisher/Traversal=Parent folder traversal is not allowed."))
    end
    assert(not path:find('//',1,true) and path:sub(-1) ~= '/', LOC("$$$/FolderTreePublisher/InvalidFilePath=Invalid file path."))
    return path
end
function M.target(sourceRoot, original, renderedName, photoId, suffix)
    local relative = M.relative(sourceRoot, original)
    assert(relative ~= '', LOC("$$$/FolderTreePublisher/ExpectedFile=Expected a file inside the source root."))
    local dir = relative:match('^(.*)/')
    assert(not renderedName:find('[/\\:]'), LOC("$$$/FolderTreePublisher/InvalidFilename=Invalid filename."))
    if suffix then
        local stem, ext = renderedName:match('^(.*)(%.[^.]*)$')
        renderedName = (stem or renderedName) .. '--' .. tostring(photoId) .. (ext or '')
    end
    return M.relativeFile((dir and dir .. '/' or '') .. renderedName)
end
-- Catalog roots are captured once per publish operation, never inferred from selected photos.
function M.catalogTarget(roots, original, renderedName, photoId, suffix)
    local selected
    for _, root in ipairs(roots) do
        local inside, relative = pcall(M.relative, root.path, original)
        if inside and relative ~= '' then
            assert(not selected, LOC("$$$/FolderTreePublisher/AmbiguousHierarchy=Ambiguous catalog folder hierarchy."))
            selected = root
        end
    end
    assert(selected, LOC("$$$/FolderTreePublisher/MissingCatalogFolder=Photo folder was not found in the catalog hierarchy: ") .. original)
    local label = M.relativeFile(selected.name)
    assert(not label:find('/', 1, true), LOC("$$$/FolderTreePublisher/InvalidRootName=Invalid top-level catalog folder name."))
    for _, root in ipairs(roots) do
        assert(root == selected or root.name:lower() ~= label:lower(),
            LOC("$$$/FolderTreePublisher/DuplicateRoots=Multiple top-level catalog folders are named ^1. Show their parent folders in Lightroom to distinguish the paths.", label))
    end
    return label .. '/' .. M.target(selected.path, original, renderedName, photoId, suffix), selected.path
end
return M
