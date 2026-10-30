# Copyright (C) 2026 Yalozo Andrey
# SPDX-License-Identifier: GPL-3.0-only

"""Run with Python + lupa (Lua 5.1), no Lightroom installation required."""
from pathlib import Path
import tempfile
import shutil
import os
import re
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
language = os.environ.get('PLUGIN_TEST_LANGUAGE', 'ru')
strings = {}
dictionary = ROOT / 'FolderTreePublisher.lrplugin' / f'TranslatedStrings_{language}.txt'
if dictionary.exists():
    for line in dictionary.read_text().splitlines():
        key, value = line[1:-1].split('=', 1)
        strings[key] = value

def loc(zstring, *args):
    key, fallback = zstring.split('=', 1)
    value = strings.get(key, fallback)
    value = value.replace('^n', '\n')
    return re.sub(r'\^([1-9])', lambda m: str(args[int(m[1])-1]), value)

lua = LuaRuntime(unpack_returned_tuples=True)
lua.globals().LOC = loc
lua.execute("package.path = ... .. '/?.lua;' .. package.path", str(ROOT / 'FolderTreePublisher.lrplugin'))
paths = lua.eval("require('Paths')")
count = 0

def equal(actual, expected):
    global count
    assert actual == expected, (actual, expected)
    count += 1

def rejects(fn, *args):
    global count
    try:
        fn(*args)
    except Exception:
        count += 1
        return
    raise AssertionError(f'Expected rejection: {args}')

equal(paths.target('/Photos', '/Photos/2026/Поездка/A.CR3', 'A.jpg', 42, False), '2026/Поездка/A.jpg')
equal(paths.target('/Photos', '/Photos/A.CR3', 'A.jpg', 42, True), 'A--42.jpg')
equal(paths.relative('C:\\Photos', 'C:\\Photos\\2026\\A.CR3'), '2026/A.CR3')
equal(paths.relative('//nas/share/photos', '//nas/share/photos/a/b.raw'), 'a/b.raw')
equal(paths.relative('/', '/Photos/a.raw'), 'Photos/a.raw')
rejects(paths.relative, '/Photos', '/Photos-other/a.raw')
rejects(paths.relative, '/Photos', '/Elsewhere/a.raw')
rejects(paths.relative, '/Photos', '/photos/a.raw')
for a, b in [('/Photos', '/Photos/out'), ('/Photos', '/Photos'), ('/Photos', '/')]:
    rejects(paths.validateRoots, a, b)
for p in ['../a', '/a', 'a/../b', 'C:/a', 'a\\b', 'a//b', 'a/']:
    rejects(paths.relativeFile, p)
rejects(paths.normalize, '/Photos/../private')


roots = lua.table_from([lua.table_from({'path': '/Users/me/Pictures/Фото', 'name': 'Фото'}),
                        lua.table_from({'path': '/Volumes/Other/Архив', 'name': 'Архив'})])
equal(paths.catalogTarget(roots, '/Users/me/Pictures/Фото/2026/A.raw', 'A.jpg', 1, False)[0], 'Фото/2026/A.jpg')
equal(paths.catalogTarget(roots, '/Volumes/Other/Архив/A.raw', 'A.jpg', 1, False)[0], 'Архив/A.jpg')
rejects(paths.catalogTarget, roots, '/Unknown/A.raw', 'A.jpg', 1, False)
duplicate = lua.table_from([lua.table_from({'path': '/Disk1/Фото', 'name': 'Фото'}),
                            lua.table_from({'path': '/Disk2/Фото', 'name': 'Фото'})])
rejects(paths.catalogTarget, duplicate, '/Disk1/Фото/A.raw', 'A.jpg', 1, False)
winroots = lua.table_from([lua.table_from({'path': 'D:/Photos', 'name': 'Photos'})])
equal(paths.catalogTarget(winroots, 'D:/Photos/Trip/A.raw', 'A.jpg', 1, True)[0], 'Photos/Trip/A--1.jpg')

mapping = lua.eval("require('CollectionPath')")
def mapped(settings):
    return mapping.apply('Фото/2026/Поездка/A.jpg', lua.table_from(settings))
equal(mapped({}), 'Фото/2026/Поездка/A.jpg')
equal(mapped({'pathPrefix': '1111', 'pathSuffix': '222', 'stripLeading': 1}), '1111/2026/Поездка/222/A.jpg')
equal(mapped({'stripLeading': 1, 'stripTrailing': 1}), '2026/A.jpg')
equal(mapped({'maxDepth': 2}), 'Фото/2026/A.jpg')
equal(mapped({'stripLeading': 100}), 'A.jpg')
equal(mapped({'stripTrailing': 100}), 'A.jpg')
equal(mapped({'pathMode': 'flat', 'pathPrefix': 'Клиенты/Анна', 'pathSuffix': 'JPEG'}), 'Клиенты/Анна/JPEG/A.jpg')
equal(mapped({'pathPrefix': 'Clients\\Anna'}), 'Clients/Anna/Фото/2026/Поездка/A.jpg')
for invalid in ['../escape', '/absolute', 'C:/absolute', 'a//b', 'a/../b', 'CON', 'a/NUL.txt', 'a?b', 'trailing.']:
    rejects(mapped, {'pathPrefix': invalid})
for invalid in [-1, 1.5, 'invalid', 101]:
    rejects(mapped, {'stripLeading': invalid})
rejects(mapped, {'pathMode': 'unknown'})

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    source, dest = base / 'source', base / 'destination'
    source.mkdir(); dest.mkdir()
    rendered = base / 'A.jpg'
    rendered.write_text('first')

    def exists(p):
        p = Path(p)
        return 'directory' if p.is_dir() else ('file' if p.is_file() else False)

    def copy(a, b):
        if Path(b).exists(): return False, 'exists'
        shutil.copyfile(a, b)
        return True

    fail_next_install = [False]
    def move(a, b):
        if fail_next_install[0] and '.ftp-new' in a:
            fail_next_install[0] = False
            return False, 'injected move failure'
        if Path(b).exists(): return False, 'exists'
        Path(a).rename(b)
        return True

    def delete(p):
        assert Path(p).is_file(), 'Must never delete directories'
        Path(p).unlink()
        return True

    def mkdir(p):
        Path(p).mkdir(parents=True, exist_ok=True)
        return True

    def unique(p):
        candidate = p
        while Path(candidate).exists(): candidate += '-1'
        return candidate

    fileutils = lua.table_from(dict(exists=exists, copy=copy, move=move, delete=delete,
        moveToTrash=delete, createAllDirectories=mkdir, chooseUniqueFileName=unique,
        resolveAllAliases=lambda p: str(Path(p).resolve()), readFile=lambda p: Path(p).read_text()))
    pathutils = lua.table_from(dict(child=lambda a,b: str(Path(a)/b), parent=lambda p: str(Path(p).parent), leafName=lambda p: Path(p).name))
    lua.globals().modules = lua.table_from({'LrFileUtils': fileutils, 'LrPathUtils': pathutils,
        'LrApplication': lua.eval('{ activeCatalog = function() return catalog end }'),
        'LrTasks': lua.eval('{ pcall = pcall }'),
        'LrDialogs': lua.eval('{ message = function(title, message, severity) lastMessage = message end }'),
        'LrShell': lua.eval('{ revealInShell = function(path) revealedPath = path end }'),
        'LrView': lua.table()})
    lua.execute("function import(name) return modules[name] end; service = require('PublishService')")
    lua.globals().source = str(source)
    lua.globals().destination = str(dest)
    lua.globals().temporary = str(rendered)
    lua.execute('''
        firstCollection = { localIdentifier = 1,
            getCollectionInfoSummary = function() return { collectionSettings = firstSettings } end,
            type = function() return 'LrPublishedCollection' end,
            getService = function() return publishService end,
            getPublishedPhotos = function() return {} end }
        publishService = {
            getChildCollections = function() return { firstCollection } end,
            getChildCollectionSets = function() return {} end }
        catalog = { getPublishedCollectionByLocalIdentifier = function(_, id)
            if id == 1 then return firstCollection end
        end, getFolders = function() return {
            { getPath = function() return source end, getName = function() return 'Фото' end }
        } end }
        settings = { destinationRoot = destination, uniqueNames = false,
            LR_publish_connectionName = 'Test', deleteCopies = true }
        original = source .. '/2026/A.CR3'
        photoUuid = 'uuid-42'
        photo = { localIdentifier = 42, getRawMetadata = function(self, key)
            if key == 'path' then return original end
            if key == 'uuid' then return photoUuid end
        end }
        rendition = { photo = photo,
            waitForRender = function() return true, temporary end,
            recordPublishedPhotoId = function(self, id) self.publishedPhotoId = id end,
            uploadFailed = function(self, message) self.failure = message end }
        context = { propertyTable = settings, publishedCollection = firstCollection,
            configureProgress = function() return { isCanceled = function() return false end, done = function() end } end,
            renditions = function() local sent = false; return function()
                if not sent then sent = true; return 1, rendition end
            end end }
        function publish() rendition.failure = nil; service.processRenderedPhotos(nil, context) end
        publish()
    ''')
    target = dest / 'Фото/2026/A.jpg'
    equal(lua.globals().rendition.failure, None)
    equal(target.read_text(), 'first')
    assert lua.globals().rendition.publishedPhotoId
    equal(list(dest.rglob('*.ftp-owner')), [])
    lua.execute('savedId = rendition.publishedPhotoId')
    rendered.write_text('second')
    lua.execute('publish()')
    equal(target.read_text(), 'second')
    # Roll back the existing destination when installing a new rendition fails.
    rendered.write_text('third')
    fail_next_install[0] = True
    lua.execute('publish()')
    equal(target.read_text(), 'second')
    assert lua.globals().rendition.failure
    # Another image cannot overwrite the first image, even with the same filename.
    lua.execute("photoUuid = 'other-photo'; rendition.publishedPhotoId = nil; publish()")
    assert lua.globals().rendition.failure
    equal(target.read_text(), 'second')
    lua.execute("photoUuid = 'uuid-42'; rendition.publishedPhotoId = savedId; publish(); original = source .. '/moved/A.CR3'; publish()")
    equal(lua.globals().rendition.failure, None)
    equal(target.exists(), False)
    target = dest / 'Фото/moved/A.jpg'
    equal(target.read_text(), 'third')
    # A destination subfolder redirect must not escape the publish root.
    (dest / 'Фото/escape').symlink_to(base, target_is_directory=True)
    lua.execute("original = source .. '/escape/A.CR3'; publish()")
    assert lua.globals().rendition.failure
    equal((base / 'A.jpg').read_text(), 'third')
    lua.execute('''
        deleted = false
        service.deletePhotosFromPublishedCollection(settings, { rendition.publishedPhotoId }, function() deleted = true end, 1)
    ''')
    equal(lua.globals().deleted, True)
    equal(target.exists(), False)
    lua.execute('''
        original = source .. '/2026/A.CR3'; rendition.publishedPhotoId = nil; publish()
        settings.deleteCopies = false
        service.deletePhotosFromPublishedCollection(settings, { rendition.publishedPhotoId }, function() end, 1)
    ''')
    equal((dest / 'Фото/2026/A.jpg').exists(), True)
    # A matching UUID sidecar alone never authorizes adoption of an existing file.
    target = dest / 'Фото/2026/A.jpg'
    marker = Path(str(target) + '.ftp-owner')
    marker.write_text('uuid-42')
    lua.execute('savedId = rendition.publishedPhotoId; rendition.publishedPhotoId = nil; publish()')
    assert lua.globals().rendition.failure
    equal(marker.exists(), True)
    # Existing Lightroom IDs migrate without creating any new sidecars.
    lua.execute('rendition.publishedPhotoId = savedId; publish()')
    equal(lua.globals().rendition.failure, None)
    equal(marker.exists(), False)
    equal(list(dest.rglob('*.ftp-owner')), [])
    # An unrelated sidecar is not deleted.
    marker.write_text('another-owner')
    lua.execute('publish()')
    equal(marker.read_text(), 'another-owner')
    marker.unlink()
    # UUID mismatch must not authorize overwrite.
    lua.execute("photoUuid = 'wrong-uuid'; publish()")
    assert lua.globals().rendition.failure
    lua.execute("photoUuid = 'uuid-42'")
    # Moving to an occupied destination must leave both images intact.
    occupied = dest / 'Фото/occupied/A.jpg'
    occupied.parent.mkdir()
    occupied.write_text('unrelated image')
    lua.execute("original = source .. '/occupied/A.CR3'; publish()")
    assert lua.globals().rendition.failure
    equal(occupied.read_text(), 'unrelated image')
    equal(target.exists(), True)
    # Failed old-file deletion must roll back a new destination and allow a retry.
    lua.execute("original = source .. '/retry/A.CR3'")
    fileutils.moveToTrash = lambda p: (False, 'injected trash failure')
    lua.execute('publish()')
    assert lua.globals().rendition.failure
    equal((dest / 'Фото/retry/A.jpg').exists(), False)
    equal(target.exists(), True)
    fileutils.moveToTrash = delete
    marker.write_text('uuid-42')
    lua.execute('publish()')
    equal(lua.globals().rendition.failure, None)
    equal(target.exists(), False)
    equal(marker.exists(), False)
    # Legacy markers are removed on deletion as well.
    target = dest / 'Фото/retry/A.jpg'
    marker = Path(str(target) + '.ftp-owner')
    marker.write_text('uuid-42')
    lua.execute('settings.deleteCopies = true; service.deletePhotosFromPublishedCollection(settings, { rendition.publishedPhotoId }, function() end, 1)')
    equal(target.exists(), False)
    equal(marker.exists(), False)
    # Two collections (one nested smart collection) share one file without sidecars.
    lua.execute("""
        original = source .. '/shared/A.CR3'
        rendition.publishedPhotoId = nil
        publish()
        firstId = rendition.publishedPhotoId
        firstCollection.getPublishedPhotos = function()
            if not firstId then return {} end
            return {{ getRemoteId = function() return firstId end }}
        end
        secondCollection = { localIdentifier = 2,
            getCollectionInfoSummary = function() return { collectionSettings = secondSettings } end,
            type = function() return 'LrPublishedCollection' end,
            isSmartCollection = function() return true end,
            getService = function() return publishService end,
            getPublishedPhotos = function()
                if not secondId then return {} end
                return {{ getRemoteId = function() return secondId end }}
            end }
        collectionSet = {
            type = function() return 'LrPublishedCollectionSet' end,
            getChildCollections = function() return { secondCollection } end,
            getChildCollectionSets = function() return {} end }
        publishService.getChildCollectionSets = function() return { collectionSet } end
        context.publishedCollection = secondCollection
        rendition.publishedPhotoId = nil
        publish()
        secondId = rendition.publishedPhotoId
    """)
    equal(lua.globals().rendition.failure, None)
    equal(lua.globals().firstId, lua.globals().secondId)
    shared = dest / 'Фото/shared/A.jpg'
    equal(shared.exists(), True)
    # Deleting from the first collection keeps the smart collection's copy.
    lua.execute("""
        deleted = false
        service.deletePhotosFromPublishedCollection(settings, { firstId }, function() deleted = true end, 1)
        firstId = nil
    """)
    equal(lua.globals().deleted, True)
    equal(shared.exists(), True)
    # A different photo cannot borrow another collection's publication path.
    lua.execute("photoUuid = 'other'; rendition.publishedPhotoId = nil; context.publishedCollection = firstCollection; publish()")
    assert lua.globals().rendition.failure
    equal(shared.read_text(), 'third')
    lua.execute("photoUuid = 'uuid-42'; context.publishedCollection = secondCollection; rendition.publishedPhotoId = secondId")
    # Removing the set containing the last reference removes the copy.
    lua.execute("service.deletePublishedCollection(settings, { publishedCollection = collectionSet, publishService = publishService }); secondId = nil")
    equal(shared.exists(), False)
    # When both collections refer to an old path, republishing one must retain it.
    lua.execute("""
        context.publishedCollection = firstCollection
        rendition.publishedPhotoId = nil
        publish()
        firstId = rendition.publishedPhotoId
        secondId = firstId
        original = source .. '/shared-moved/A.CR3'
        publish()
        firstId = rendition.publishedPhotoId
    """)
    equal(lua.globals().rendition.failure, None)
    equal(shared.exists(), True)
    equal((dest / 'Фото/shared-moved/A.jpg').exists(), True)
    lua.execute("""
        context.publishedCollection = secondCollection
        rendition.publishedPhotoId = secondId
        publish()
        secondId = rendition.publishedPhotoId
    """)
    equal(lua.globals().rendition.failure, None)
    equal(shared.exists(), False)
    # Removing a collection keeps a file referenced in another collection.
    lua.execute("service.deletePublishedCollection(settings, { publishedCollection = firstCollection, publishService = publishService }); firstId = nil")
    equal((dest / 'Фото/shared-moved/A.jpg').exists(), True)
    # Keep-copies preference also applies to deleting entire collections/sets.
    lua.execute("settings.deleteCopies = false; service.deletePublishedCollection(settings, { publishedCollection = collectionSet, publishService = publishService })")
    equal((dest / 'Фото/shared-moved/A.jpg').exists(), True)
    equal(list(dest.rglob('*.ftp-owner')), [])
    # Per-collection settings can give the same photo independent destinations.
    lua.execute("""
        settings.deleteCopies = true
        firstId = nil; secondId = nil
        original = source .. '/custom/A.CR3'
        firstSettings = { pathMode = 'flat', pathPrefix = 'Client A' }
        secondSettings = { stripLeading = 1, pathPrefix = 'Client B', pathSuffix = 'JPEG' }
        context.publishedCollection = firstCollection; rendition.publishedPhotoId = nil
        publish(); firstId = rendition.publishedPhotoId
        context.publishedCollection = secondCollection; rendition.publishedPhotoId = nil
        publish(); secondId = rendition.publishedPhotoId
    """)
    equal(lua.globals().rendition.failure, None)
    equal((dest / 'Client A/A.jpg').exists(), True)
    equal((dest / 'Client B/custom/JPEG/A.jpg').exists(), True)
    lua.execute("""
        firstSettings.pathPrefix = 'Client A revised'
        context.publishedCollection = firstCollection; rendition.publishedPhotoId = firstId
        publish(); firstId = rendition.publishedPhotoId
    """)
    equal(lua.globals().rendition.failure, None)
    equal((dest / 'Client A/A.jpg').exists(), False)
    equal((dest / 'Client A revised/A.jpg').exists(), True)
    equal((dest / 'Client B/custom/JPEG/A.jpg').exists(), True)
    lua.execute("service.deletePublishedCollection(settings, { publishedCollection = firstCollection, publishService = publishService }); firstId = nil")
    equal((dest / 'Client A revised/A.jpg').exists(), False)
    equal((dest / 'Client B/custom/JPEG/A.jpg').exists(), True)
    # Saving path settings marks existing publications for republish via a write gate.
    lua.execute("""
        catalog.withPrivateWriteAccessDo = function() error('Private access is insufficient for setEditedFlag') end
        catalog.withWriteAccessDo = function(_, name, action)
            assert(type(name) == 'string' and name ~= '')
            fullWriteAccess = true
            action()
            fullWriteAccess = false
        end
        local pub = { getRemoteId = function() return secondId end,
            setEditedFlag = function(_, value)
                assert(fullWriteAccess, 'setEditedFlag requires withWriteAccessDo')
                republishFlag = value
            end }
        local c = { getPublishedPhotos = function() return {pub} end }
        service.updateCollectionSettings(settings, { collectionSettings = secondSettings, publishedCollection = c })
    """)
    equal(lua.globals().republishFlag, True)
    # Lightroom supplies the rendered video filename and bytes (transcoding is SDK-owned).
    video = base / 'Clip.mp4'
    video.write_bytes(b'video fixture: rendered MP4')
    lua.globals().temporary = str(video)
    lua.execute("""
        assert(service.canExportVideo)
        firstSettings = { pathPrefix = 'Movies', stripLeading = 1 }
        context.publishedCollection = firstCollection
        original = source .. '/2026/Clip.MOV'
        photoUuid = 'video-uuid'; photo.localIdentifier = 99
        settings.uniqueNames = true
        rendition.publishedPhotoId = nil
        publish()
    """)
    equal(lua.globals().rendition.failure, None)
    published_video = dest / 'Movies/2026/Clip--99.mp4'
    equal(published_video.read_bytes(), video.read_bytes())
    video.write_bytes(b'video fixture: updated MP4')
    lua.execute('publish()')
    equal(published_video.read_bytes(), video.read_bytes())
    # A video rendering error retains the old copy and publication ID.
    lua.execute("""
        videoId = rendition.publishedPhotoId
        renderVideo = rendition.waitForRender
        rendition.waitForRender = function() return false, 'Video encoder failure' end
        publish()
    """)
    assert 'Video encoder failure' in lua.globals().rendition.failure
    equal(lua.globals().rendition.publishedPhotoId, lua.globals().videoId)
    equal(published_video.read_bytes(), video.read_bytes())
    # Original-format output retains MOV, removing the previous MP4 after success.
    original_video = base / 'Clip.MOV'
    original_video.write_bytes(b'video fixture: original MOV')
    lua.globals().temporary = str(original_video)
    lua.execute('rendition.waitForRender = renderVideo; publish()')
    equal(lua.globals().rendition.failure, None)
    equal(published_video.exists(), False)
    published_video = dest / 'Movies/2026/Clip--99.MOV'
    equal(published_video.read_bytes(), original_video.read_bytes())
    lua.execute('service.deletePhotosFromPublishedCollection(settings, { rendition.publishedPhotoId }, function() end, 1)')
    equal(published_video.exists(), False)
    equal(list(dest.rglob('*.ftp-owner')), [])
    # Collection navigation uses its destination folder without needing a remote URL.
    lua.execute('service.goToPublishedCollection(settings, {})')
    equal(lua.globals().revealedPath, str(dest.resolve()))
    equal(lua.globals().lastMessage, None)
    lua.execute('revealedPath = nil')
    # Missing destination volume must be an error, not recreated.
    shutil.rmtree(dest)
    rejects(lua.globals().publish)
    equal(dest.exists(), False)
    lua.execute('service.goToPublishedCollection(settings, {})')
    equal(lua.globals().revealedPath, None)
    assert loc('$$$/FolderTreePublisher/DestinationUnavailable=The publication folder is unavailable. Connect the drive or create the folder.') in lua.globals().lastMessage
    equal(dest.exists(), False)

# Build About using a view-factory stub and exercise all external-link actions.
about_lua = LuaRuntime(unpack_returned_tuples=True)
about_lua.globals().LOC = loc
about_lua.execute("package.path = ... .. '/?.lua;' .. package.path", str(ROOT / 'FolderTreePublisher.lrplugin'))
about_lua.execute("""
    opened = {}
    import = function(name)
        assert(name == 'LrHttp')
        return { openUrlInBrowser = function(url) table.insert(opened, url) end }
    end
    _PLUGIN = { resourceId = function(_, name) return name end }
    local factory = setmetatable({}, { __index = function(_, name)
        if name == 'control_spacing' or name == 'label_spacing' then
            return function() return 6 end
        end
        return function(_, spec) spec.kind = name; return spec end
    end })
    about = require('PluginInfoProvider').sectionsForTopOfDialog(factory, {})
    titles = {}
    local function visit(node)
        if node.title then table.insert(titles, node.title) end
        if node.kind == 'push_button' then node.action() end
        for _, child in ipairs(node) do
            if type(child) == 'table' then visit(child) end
        end
    end
    visit(about)
""")
equal(list(about_lua.globals().opened.values()), [
    'https://github.com/Yalozo', 'mailto:avyalozo@gmail.com',
    'https://www.gnu.org/licenses/gpl-3.0.html',
])
about_titles = list(about_lua.globals().titles.values())
for expected in ['Yalozo Andrey', 'avyalozo@gmail.com', 'GPL-3.0-only']:
    equal(any(expected in title for title in about_titles), True)

for path in (ROOT / 'FolderTreePublisher.lrplugin').glob('*.lua'):
    lua.execute('assert(loadstring(...))', path.read_text())
    count += 1
print(f'PASS: {count} assertions plus publish lifecycle, collision, rollback and symlink checks (Lua 5.1)')
