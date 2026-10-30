-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

return {
    LrSdkVersion = 6.0,
    LrSdkMinimumVersion = 6.0,
    LrToolkitIdentifier = 'ws.sarov.folder-tree-publisher',
    LrPluginName = 'Folder Tree Publisher',
    LrPluginInfoProvider = 'PluginInfoProvider.lua',
    VERSION = { major = 0, minor = 8, revision = 0, build = 11 },
    LrExportServiceProvider = {
        title = 'Folder Tree Publisher',
        file = 'PublishService.lua',
    },
}
