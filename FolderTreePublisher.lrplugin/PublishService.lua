-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

local Application = import 'LrApplication'
local F = import 'LrFileUtils'
local P = import 'LrPathUtils'
local Tasks = import 'LrTasks'
local Dialogs = import 'LrDialogs'
local View = import 'LrView'
local Shell = import 'LrShell'
local Paths = require 'Paths'
local References = require 'CollectionReferences'
local CollectionPath = require 'CollectionPath'
local Service = {
    small_icon = 'icon-small.png',
    supportsIncrementalPublish = 'only',
    canExportVideo = true,
    hideSections = { 'exportLocation', 'fileNaming' },
    allowFileFormats = { 'JPEG', 'TIFF', 'PSD', 'PNG' },
    exportPresetFields = {
        { key = 'destinationRoot', default = '' },
        { key = 'uniqueNames', default = true },
        { key = 'deleteCopies', default = false },
    },
}
local function check(ok, message)
    if not ok then error(tostring(message or LOC("$$$/FolderTreePublisher/FileOperationError=File operation failed.")), 0) end
end
local function native(root, relative)
    local result = root
    for part in Paths.relativeFile(relative):gmatch('[^/]+') do result = P.child(result, part) end
    return result
end
local function destinationRoot(s)
    Paths.normalize(s.destinationRoot)
    check(F.exists(s.destinationRoot) == 'directory', LOC("$$$/FolderTreePublisher/DestinationUnavailable=The publication folder is unavailable. Connect the drive or create the folder."))
    return F.resolveAllAliases(s.destinationRoot)
end
local function catalogRoots()
    local result = {}
    for _, folder in ipairs(Application.activeCatalog():getFolders()) do
        -- getFolders returns the roots of the catalog folder hierarchy.
        local name = folder:getName()
        -- A drive may itself be a catalog root (e.g. D: on Windows).
        if name:match('^%a:$') then name = name:sub(1, 1) end
        if name == '/' then name = 'Root' end
        result[#result + 1] = { path = folder:getPath(), name = name }
    end
    check(#result > 0, LOC("$$$/FolderTreePublisher/NoCatalogFolders=The catalog has no folders to publish."))
    return result
end
local function safeTarget(root, relative)
    local target = native(root, relative)
    -- Check existing parents too, before creating directories or touching a file.
    local resolved = F.resolveAllAliases(target)
    Paths.relative(F.resolveAllAliases(root), resolved)
    return target
end
-- Legacy sidecars are removed only when their contents match a recorded publication.
-- New publications store their identity solely in Lightroom.
local function cleanLegacyOwner(root, relative, owner)
    local marker = native(root, relative) .. '.ftp-owner'
    if F.exists(marker) == 'file' then
        Paths.relative(F.resolveAllAliases(root), F.resolveAllAliases(marker))
        if F.readFile(marker) == owner then check(F.delete(marker)) end
    end
end
local function removePublished(root, relative, owner)
    local target = safeTarget(root, relative)
    if F.exists(target) then
        check(F.exists(target) == 'file', LOC("$$$/FolderTreePublisher/ExpectedFileNotFolder=A folder was found where a file was expected."))
        check(F.moveToTrash(target))
    end
    cleanLegacyOwner(root, relative, owner)
end
local decode = References.decode
function Service.startDialog(s)
    s.ftpRootsEditable = not s.LR_editingExistingPublishConnection
    local function validate()
        local ok, err = pcall(Paths.normalize, s.destinationRoot)
        s.LR_cantExportBecause = not ok and tostring(err) or nil
    end
    s:addObserver('destinationRoot', validate)
    validate()
end
function Service.sectionsForTopOfDialog(f, s)
    local function folderRow(label, field)
        return f:row {
            f:static_text { title = label, width = 150 },
            f:edit_field { value = View.bind(field), width_in_chars = 42, enabled = View.bind('ftpRootsEditable') },
            f:push_button { title = LOC("$$$/FolderTreePublisher/Choose=Choose..."), enabled = View.bind('ftpRootsEditable'), action = function()
                local selected = Dialogs.runOpenPanel { title = label, canChooseFiles = false,
                    canChooseDirectories = true, allowsMultipleSelection = false }
                if selected then s[field] = selected[1] end
            end },
        }
    end
    return {{ title = LOC("$$$/FolderTreePublisher/FolderStructure=Folder structure"), bind_to_object = s,
        folderRow(LOC("$$$/FolderTreePublisher/PublishFolder=Publication folder"), 'destinationRoot'),
        f:checkbox { title = LOC("$$$/FolderTreePublisher/UniqueNames=Append photo ID to filenames (avoid collisions and support virtual copies)"), value = View.bind('uniqueNames') },
        f:checkbox { title = LOC("$$$/FolderTreePublisher/DeleteCopies=Move copies to Trash when removed from publication"), value = View.bind('deleteCopies') },
        f:static_text { title = LOC("$$$/FolderTreePublisher/HierarchyHelp=Use the catalog folder hierarchy, including the top-level folder.^nCreate a new service to use a different destination."), width_in_chars = 75, height_in_lines = 2 },
    }}
end
-- Local collections have a disk destination, not a web URL.
function Service.goToPublishedCollection(s, _)
    local ok, err = Tasks.pcall(function()
        Shell.revealInShell(destinationRoot(s))
    end)
    if not ok then
        Dialogs.message(LOC("$$$/FolderTreePublisher/RevealError=Could not show the publication folder"), tostring(err), 'warning')
    end
end
Service.viewForCollectionSettings = CollectionPath.view
function Service.updateCollectionSettings(_, info)
    CollectionPath.settings(info.collectionSettings)
    if not info.publishedCollection then return end
    local photos = info.publishedCollection:getPublishedPhotos()
    Application.activeCatalog():withWriteAccessDo(LOC("$$$/FolderTreePublisher/UpdatePath=Update collection publication path"), function()
        for _, published in ipairs(photos) do
            if published:getRemoteId() then published:setEditedFlag(true) end
        end
    end)
end
function Service.getCollectionBehaviorInfo()
    return { defaultCollectionName = LOC("$$$/FolderTreePublisher/DefaultCollection=Photos"), defaultCollectionCanBeDeleted = false,
        canAddCollection = true }
end
function Service.metadataThatTriggersRepublish()
    return { default = true }
end
function Service.updateExportSettings(s)
    s.LR_renamingTokensOn = false
end
function Service.processRenderedPhotos(_, context)
    local s = context.propertyTable
    local destinationRoot = destinationRoot(s)
    local hierarchy = catalogRoots()
    local collection = context.publishedCollection
    check(collection, LOC("$$$/FolderTreePublisher/MissingCollection=Could not identify the collection being published."))
    local pathSettings = CollectionPath.settings(collection:getCollectionInfoSummary().collectionSettings)
    local references = References.index(collection:getService(), { [tostring(collection.localIdentifier)] = true })
    local progress = context:configureProgress { title = LOC("$$$/FolderTreePublisher/Progress=Publishing folder structure") }
    for _, rendition in context:renditions { stopIfCanceled = true } do
        if progress:isCanceled() then break end
        if not rendition.wasSkipped then
            local ok, err = Tasks.pcall(function()
                local rendered, temporary = rendition:waitForRender()
                check(rendered, temporary)
                local photo = rendition.photo
                local owner = tostring(photo:getRawMetadata('uuid'))
                check(owner ~= 'nil', LOC("$$$/FolderTreePublisher/MissingUuid=Could not retrieve the photo UUID."))
                local original = photo:getRawMetadata('path')
                local relative, sourceRoot = Paths.catalogTarget(hierarchy, original, P.leafName(temporary), photo.localIdentifier, s.uniqueNames)
                Paths.validateRoots(F.resolveAllAliases(sourceRoot), destinationRoot)
                Paths.relative(F.resolveAllAliases(sourceRoot), F.resolveAllAliases(original))
                relative = CollectionPath.apply(relative, pathSettings)
                local target = safeTarget(destinationRoot, relative)
                local oldOwner, oldRelative
                if rendition.publishedPhotoId then
                    oldOwner, oldRelative = decode(rendition.publishedPhotoId)
                    check(oldOwner == owner, LOC("$$$/FolderTreePublisher/ChangedUuid=The photo identifier has changed."))
                end
                local shared = References.authorized(references, relative, owner)
                if F.exists(target) then
                    check(oldRelative == relative or shared, LOC("$$$/FolderTreePublisher/UnlinkedFile=This file exists but is not linked to this Lightroom publication: ") .. target)
                end
                check(F.createAllDirectories(P.parent(target)))
                safeTarget(destinationRoot, relative)
                local staging = F.chooseUniqueFileName(target .. '.ftp-new')
                check(F.copy(temporary, staging))
                local backup
                if F.exists(target) then
                    check(F.exists(target) == 'file', LOC("$$$/FolderTreePublisher/ExpectedFileNotFolder=A folder was found where a file was expected."))
                    backup = F.chooseUniqueFileName(target .. '.ftp-backup')
                    local moved, message = F.move(target, backup)
                    if not moved then F.delete(staging); check(false, message) end
                end
                local moved, message = F.move(staging, target)
                if not moved then
                    if backup then F.move(backup, target) end
                    F.delete(staging)
                    check(false, message)
                end
                -- Keep the previous destination until all follow-up filesystem operations succeed.
                local completed, completionError = Tasks.pcall(function()
                    if oldRelative then
                        if oldRelative ~= relative then
                            if not References.referenced(references, oldRelative) then
                                removePublished(destinationRoot, oldRelative, owner)
                            end
                        else
                            cleanLegacyOwner(destinationRoot, oldRelative, owner)
                        end
                    end
                end)
                if not completed then
                    F.delete(target)
                    if backup then F.move(backup, target) end
                    error(completionError, 0)
                end
                rendition:recordPublishedPhotoId('FTP1|' .. owner .. '|' .. relative)
                if backup then check(F.delete(backup)) end
            end)
            if not ok then rendition:uploadFailed(tostring(err)) end
        end
    end
    progress:done()
end
function Service.deletePhotosFromPublishedCollection(s, ids, deletedCallback, localCollectionId)
    if s.deleteCopies then
        local collection = Application.activeCatalog():getPublishedCollectionByLocalIdentifier(localCollectionId)
        check(collection, LOC("$$$/FolderTreePublisher/MissingDeleteCollection=Could not identify the collection for safe removal of copies."))
        local references = References.index(collection:getService(), { [tostring(localCollectionId)] = true })
        local destination = destinationRoot(s)
        for _, id in ipairs(ids) do
            local owner, relative = decode(id)
            if not References.referenced(references, relative) then removePublished(destination, relative, owner) end
            deletedCallback(id)
        end
    else
        for _, id in ipairs(ids) do deletedCallback(id) end
    end
end
-- Collection names organize Lightroom only; they do not name directories on disk.
function Service.renamePublishedCollection() end
function Service.reparentPublishedCollection() end
function Service.deletePublishedCollection(s, info)
    if not s.deleteCopies then return end
    local collection = info.publishedCollection
    check(collection and info.publishService, LOC("$$$/FolderTreePublisher/MissingDeletedCollection=Could not identify the collection being deleted."))
    local collections
    if collection:type() == 'LrPublishedCollectionSet' then
        collections = References.collections(collection)
    else
        collections = { collection }
    end
    local excluded = {}
    for _, child in ipairs(collections) do excluded[tostring(child.localIdentifier)] = true end
    local references = References.index(info.publishService, excluded)
    local destination = destinationRoot(s)
    local removed = {}
    for _, child in ipairs(collections) do
        for _, published in ipairs(child:getPublishedPhotos()) do
            local id = published:getRemoteId()
            if id and id ~= '' then
                local owner, relative = decode(id)
                if not removed[relative] and not References.referenced(references, relative) then
                    removePublished(destination, relative, owner)
                    removed[relative] = true
                end
            end
        end
    end
end
-- Lightroom tasks can yield while rendering or moving files. Serialize mutations so
-- another collection cannot change shared references between a scan and a deletion.
local busy = false
for _, name in ipairs { 'processRenderedPhotos', 'deletePhotosFromPublishedCollection', 'deletePublishedCollection' } do
    local operation = Service[name]
    Service[name] = function(...)
        local args = { ... }
        local count = select('#', ...)
        while busy do Tasks.sleep(0.1) end
        busy = true
        local ok, err = Tasks.pcall(function() operation(unpack(args, 1, count)) end)
        busy = false
        if not ok then error(err, 0) end
    end
end
return Service
