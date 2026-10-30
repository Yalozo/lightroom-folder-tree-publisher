-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

-- Reference counts come from Lightroom; no files or separate database are created.
local M = {}
function M.decode(id)
    local owner, relative = tostring(id):match('^FTP1|([^|]+)|(.+)$')
    assert(owner and relative, LOC("$$$/FolderTreePublisher/UnknownPublication=Unknown publication identifier."))
    return owner, require('Paths').relativeFile(relative)
end
function M.collections(container, result)
    result = result or {}
    for _, collection in ipairs(container:getChildCollections()) do
        result[#result + 1] = collection
    end
    for _, set in ipairs(container:getChildCollectionSets()) do M.collections(set, result) end
    return result
end
function M.index(service, excluded)
    assert(service, LOC("$$$/FolderTreePublisher/MissingService=Could not identify the publish service."))
    local result = {}
    for _, collection in ipairs(M.collections(service)) do
        if not excluded[tostring(collection.localIdentifier)] then
            for _, published in ipairs(collection:getPublishedPhotos()) do
                local id = published:getRemoteId()
                if id and id ~= '' then
                    local owner, relative = M.decode(id)
                    local key = relative:lower()
                    result[key] = result[key] or {}
                    result[key][owner] = true
                end
            end
        end
    end
    return result
end
function M.referenced(index, relative)
    return index[relative:lower()] ~= nil
end
function M.authorized(index, relative, owner)
    local owners = index[relative:lower()]
    if not owners then return false end
    for other in pairs(owners) do
        assert(other == owner, LOC("$$$/FolderTreePublisher/PathInUse=Another photo in this service uses this path: ") .. relative)
    end
    return owners[owner] == true
end
return M
