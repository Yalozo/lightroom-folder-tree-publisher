# Folder Tree Publisher

![Folder Tree Publisher](FolderTreePublisher.lrplugin/icon.png)

Publish photos and videos from **Adobe Lightroom Classic** to disk while preserving the catalog's folder hierarchy. Customize the output path for each regular or smart published collection.

[Русская инструкция](README.ru.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Translations](TRANSLATING.md) · [Illustrated guide](docs/USER_GUIDE.md) · [GitHub](https://github.com/Yalozo/lightroom-folder-tree-publisher) · [Releases](https://github.com/Yalozo/lightroom-folder-tree-publisher/releases) · [Issues](https://github.com/Yalozo/lightroom-folder-tree-publisher/issues)

**Beta:** automated tests cover Lua logic and simulated Lightroom callbacks. Compatibility with specific Lightroom/OS releases, actual video encoding, and the complete UI still need validation. This plug-in targets Lightroom Classic, not the cloud-based Lightroom application.

## Features

- Folder hierarchy read directly from the catalog; no source-root setting.
- Regular collections, smart collections, and nested collection sets.
- Per-collection path prefixes/suffixes, trimming, depth limits, and flat-folder mode.
- Standard Lightroom photo and video export settings.
- Republish changed files and optionally move removed copies to Trash.
- Shared-file protection when the same photo appears in several collections.
- Optional photo IDs in filenames for collisions and virtual copies.
- Russian and English UI; English fallback for untranslated languages.
- No `.ftp-owner` files created by current versions.

## Install

1. Download the **FolderTreePublisher versioned ZIP** from this repository's Releases page. Use the plug-in ZIP rather than GitHub's automatically generated source archive.
2. Extract it to a permanent location.
3. In Lightroom Classic, open **File → Plug-in Manager → Add**.
4. Select the extracted `FolderTreePublisher.lrplugin` folder.
5. Open **Library → Publish Services → Folder Tree Publisher → Set Up**.
6. Choose a separate, existing destination folder and set the desired export format, size, quality, and metadata options.
7. Save, add photos to the default collection, then click **Publish**.

For updates, replace the plug-in folder and restart Lightroom. Existing collection settings and publication IDs are retained. Normal use needs neither Python nor a separate Lua installation.

## Folder mapping

If the catalog has a top-level folder named `Photos`, the source file `/Users/me/Pictures/Photos/2026/Trip/IMG_001.CR3` is published as:

```text
<destination>/Photos/2026/Trip/IMG_001--123.jpg
```

`123` is the photo's local catalog ID; disable the filename-ID option to keep `IMG_001.jpg`. The filesystem prefix outside the catalog root is omitted. Duplicate top-level folder names are rejected rather than merged; show their parent folders in Lightroom to distinguish them.

## Collections and custom paths

Right-click the publish service to create a **Published Collection**, **Published Smart Collection**, or **Published Collection Set**. Smart collections use Lightroom's selection rules. Collection sets organize the UI; their names do not become output directories.

Create or edit a collection to configure its publication path:

| Setting | Effect |
| --- | --- |
| Keep hierarchy / flat folder | Preserve source folders or discard them |
| Subfolder before hierarchy | Add a prefix such as `Clients/Anna` |
| Remove levels from start/end | Trim source folder components |
| Keep first levels | Limit the remaining hierarchy; 0 means unlimited |
| Subfolder after hierarchy | Add a suffix such as `JPEG` before the filename |

Order: trim start → trim end → limit depth → add prefix/suffix. Rules affect folders only. The preview uses a clearly labeled sample path, not a selected photo. Settings are independent for each collection and are not inherited from sets.

Saving collection settings marks existing publications for republishing. Click **Publish** to apply them. Old copies move to Trash after successful replacement only if no other collection references them. The same photo can have separate output files when two collections use different paths.

## Video

In the service's **Video** section, enable **Include Video Files** and choose a format and quality. Lightroom supplies the available formats and performs encoding. The plug-in copies its output, preserving its actual extension. Photo-specific JPEG/TIFF settings do not limit video. Unsupported codecs are not added by this plug-in.

## File lifecycle

Use a dedicated output folder for each service. Source and destination roots must not overlap. Do not publish into the same destination from different catalogs/services.

The plug-in stores the photo UUID and published relative path in Lightroom. A pre-existing file without a matching publication record is not overwritten. Do not replace managed copies with unrelated files at the same path: the plug-in identifies them by the recorded path, not their content.

Removal keeps disk copies by default. Enable **Move copies to Trash when removed from publication** to delete them during Lightroom's publish cycle. A file referenced in another collection is retained until its last publication reference is removed. Empty folders remain. If Trash is unavailable on a network volume, deletion fails rather than becoming permanent.

Changes to source folders or the catalog's top-level hierarchy may require **Mark to Republish**. Old `.ftp-owner` files from versions before 0.3 are removed during republishing only when their UUID matches the recorded publication. There is no background disk scan.

File replacement includes rollback attempts but is not a crash-proof filesystem transaction. Interrupted operations can leave `.ftp-new` or `.ftp-backup` files; preserve these while investigating recovery.

## Limits and support

Network destinations must be mounted as ordinary folders. No FTP/SFTP transport, photo-original/XMP export, Smart Preview backup mode, or import of Jeffrey's plug-in settings is implemented. Collections use the service's shared export settings, not individual format/quality settings.

Report bugs through **Issues**, including plug-in version, Lightroom version, OS, relevant settings, and exact error text. Remove private information from screenshots. Start with a few files in a separate output folder before publishing a large library.

This is an independent implementation inspired by [Jeffrey's Folder Publisher](https://regex.info/blog/lightroom-goodies/folder-publisher). It is not affiliated with Jeffrey Friedl or Adobe and does not include their plug-in code or SDK files.

## Author and license

Developed by **Yalozo Andrey** · [GitHub: Yalozo](https://github.com/Yalozo) · [avyalozo@gmail.com](mailto:avyalozo@gmail.com).

Copyright (C) 2026 Yalozo Andrey. Licensed under [GNU GPL version 3 only](LICENSE) (`GPL-3.0-only`). You may use, modify, and redistribute this software, including commercially, under that license. When distributing modified versions, comply with GPLv3, including its corresponding-source requirements. The software is provided without warranty. See LICENSE for the full terms.
