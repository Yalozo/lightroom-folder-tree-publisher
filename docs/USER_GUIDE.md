# Folder Tree Publisher: illustrated guide

[Русский](USER_GUIDE.ru.md) · [Overview and limitations](../README.md)

These screenshots show plug-in 0.8.0 in Russian Lightroom Classic. The English instructions below explain the corresponding controls. Paths shown belong to the demonstration setup; choose your own destination.

## 1. Install the plug-in

Extract the release archive into a permanent folder. In Lightroom, open **File → Plug-in Manager → Add** and select `FolderTreePublisher.lrplugin`. Select **Folder Tree Publisher** and check that it is enabled and working. The About panel shows its version, author, contacts, and license. Click **Done**.

![Plug-in Manager with Folder Tree Publisher enabled](screenshots/01-plugin-manager.png)

## 2. Configure a publish service

In the **Library** module, find **Publish Services** and set up **Folder Tree Publisher**. Enter a service description and choose a dedicated existing publication folder during initial setup. Source folder hierarchy comes from the Lightroom catalog automatically.

The destination field is locked after service creation, as shown here. Create another service to publish to a different destination.

- Enable **Append photo ID to filenames** to avoid filename collisions and support virtual copies.
- Enable **Move copies to Trash when removed from publication** if you want removed publications to delete their managed copies during the next publish cycle. With this disabled, disk copies remain. Originals are preserved.

Configure image format, quality, size, and metadata, then save. Export settings are shared by collections within a service.

![Service description, destination, and folder settings](screenshots/02-publish-settings.png)

## 3. Enable video

Expand **Video** and check **Include Video Files**. Without it, Lightroom skips videos and may report “This file is a video file”. Choose an available format and quality. **DPX** is selected in the screenshot as an example; it is not required. For an initial check, choose **Original** if available. The JPEG controls below apply to still photographs.

Lightroom performs encoding; the plug-in places the output using the collection's path rules. Save the service settings.

![Include Video Files enabled with video format and quality controls](screenshots/03-video-settings.png)

## 4. Create a regular published collection

Use the service's context menu to create a published collection and give it a name. Add photographs from the Lightroom library.

The collection path controls let you preserve the source hierarchy or use a flat layout, prepend a subfolder, strip leading or trailing folder levels, limit the remaining depth, and append a subfolder before the filename. Zero in the depth limit means all levels. Processing order is: strip leading levels → strip trailing levels → limit depth → add subfolders. Subfolders are relative to the service destination; use `/` between nested folders.

Here, `Portfolio` is prepended and the other controls retain their defaults. The example path becomes `Portfolio/Фото/2026/Поездка/IMG_001.jpg` inside the destination. The preview uses a sample path, not a selected photograph.

Click **Create**. Changing an existing collection's path marks its publications for updating; click **Publish** to apply the changes to disk.

![Regular collection with Portfolio prepended to the folder hierarchy](screenshots/04-collection-path.png)

## 5. Create a smart published collection

Create a smart published collection using the service's context menu. Lightroom selects photographs automatically from its rules. Here, **all** rules must match: a rating of **at least four stars** and a **red color label**.

Path settings work just like a regular collection's. This example prepends `4stars`. The collection's name does not itself create a destination folder. Click **Create**, then **Publish** to write the matching files to disk; automatic selection does not automatically publish files.

![Smart collection with rating and red-label rules and a 4stars path prefix](screenshots/05-smart-collection.png)

## 6. Publish

Open a collection, add files to a regular collection or review the smart collection's matching files. The screenshot shows seven items, including two videos identified by duration badges. Click **Publish** above the grid or below the left panel and wait for processing to finish.

Use the same button for subsequent updates. To force an update when needed, select files and use **Mark to Republish** in the context menu.

![Published collection with photographs, videos, and the Publish button](screenshots/06-publish-collection.png)

## 7. Open the destination

Right-click the published collection and choose **Go to Published Collection** (highlighted in the screenshot). This plug-in opens the service's destination root in Finder on macOS or Explorer on Windows. Expand the collection's subfolders inside it.

![Go to Published Collection in the context menu](screenshots/07-open-destination.png)

## 8. Check the output

In Finder, use list view and expand the folders. Compare the output with the collection's path rules.

The illustration below uses sample data and matches the **`Portfolio`** prefix from section 4. It is an edited demonstration, not a capture of an actual export. Sidebar details and the home-folder path have been removed.

```text
lr_export/
└── Portfolio/
    └── Фото/
        └── 2026/
            └── Поездка/
                ├── IMG_001--123.jpg
                ├── IMG_002--124.jpg
                └── Clip--125.mov
```

The `--123`, `--124`, and `--125` suffixes illustrate the filename-ID option. The collection settings preview uses a sample filename without that suffix. No trailing subfolder is configured. MOV is used for this video example; actual output depends on the Lightroom video settings.

![Demonstration of Portfolio/Фото/2026/Поездка with photos and a video](screenshots/08-finder-result.png)

After publishing, check your actual destination and open the video with a suitable application.

## Troubleshooting

- **“This file is a video file”**: check **Include Video Files** in the service settings.
- **Destination unavailable**: connect the drive and check that the folder exists.
- **Existing file not linked to publication**: check for a conflict or use an unused destination; inspect unknown files before deleting them.
- For support, include plug-in, Lightroom, and OS versions, the exact error, and the collection settings.
