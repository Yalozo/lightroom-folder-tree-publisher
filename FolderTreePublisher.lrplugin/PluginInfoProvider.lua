-- Copyright (C) 2026 Yalozo Andrey
-- SPDX-License-Identifier: GPL-3.0-only

local LrHttp = import 'LrHttp'
local developer = require 'DeveloperInfo'
local info = require 'Info'
local version = info.VERSION
return {
    sectionsForTopOfDialog = function(f, _)
        return {{
            title = LOC("$$$/FolderTreePublisher/About=About this plug-in"),
            synopsis = LOC("$$$/FolderTreePublisher/Synopsis=Publish while preserving folder structure"),
            f:row {
                spacing = f:control_spacing(),
                f:picture { value = _PLUGIN:resourceId('icon.png') },
                f:column {
                    spacing = f:label_spacing(),
                    f:static_text { title = 'Folder Tree Publisher', font = '<system/bold>' },
                    f:static_text { title = string.format(LOC("$$$/FolderTreePublisher/Version=Version %d.%d.%d"), version.major, version.minor, version.revision) },
                    f:static_text {
                        title = LOC("$$$/FolderTreePublisher/Description=Publish photos and videos from regular and smart collections^nto disk, preserving the Lightroom catalog folder hierarchy.^nUpdate copies and optionally move removed files to Trash."),
                        width_in_chars = 60,
                        height_in_lines = 3,
                    },
                    f:static_text { title = LOC("$$$/FolderTreePublisher/Developer=Developer: ^1", developer.name) },
                    f:static_text { title = LOC("$$$/FolderTreePublisher/Contact=Contact: ^1", developer.email) },
                    f:static_text { title = LOC("$$$/FolderTreePublisher/License=License: ^1", developer.license) },
                    f:static_text { title = developer.copyright },
                    f:static_text {
                        title = LOC("$$$/FolderTreePublisher/Warranty=Free software, provided without warranty."),
                        width_in_chars = 60,
                    },
                    f:row {
                        spacing = f:control_spacing(),
                        f:push_button {
                            title = 'GitHub',
                            action = function() LrHttp.openUrlInBrowser(developer.github) end,
                        },
                        f:push_button {
                            title = LOC("$$$/FolderTreePublisher/WriteEmail=Email developer"),
                            action = function() LrHttp.openUrlInBrowser('mailto:' .. developer.email) end,
                        },
                        f:push_button {
                            title = LOC("$$$/FolderTreePublisher/ReadLicense=Read license"),
                            action = function() LrHttp.openUrlInBrowser(developer.licenseUrl) end,
                        },
                    },
                },
            },
        }}
    end,
}
