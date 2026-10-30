# Preparing the first GitHub release

Repository: [https://github.com/Yalozo/lightroom-folder-tree-publisher](https://github.com/Yalozo/lightroom-folder-tree-publisher).

Suggested description: “Lightroom Classic publish service preserving catalog folder hierarchy, with per-collection paths and video support.”

Suggested topics: `lightroom`, `lightroom-classic`, `lightroom-plugin`, `lua`, `photography`, `publish-service`.

1. Run the checks in CONTRIBUTING.md and test the plug-in in Lightroom with a small separate destination. Record Lightroom and OS versions; automated tests use mocked APIs.
2. Confirm the public author/email and GPL-3.0-only terms. The repository already contains LICENSE and README files; do not generate replacements on GitHub.
3. Create the repository under Yalozo, upload the source tree, and check that the GitHub Actions workflow passes. Generated `dist/` files, personal catalogs, and photographs must not be committed.
4. Update the documentation with the actual repository and Releases links. The About GitHub button currently opens the author's profile; its URL is in DeveloperInfo.lua.
5. Run `python tools/build_release.py`. For this first version, create a **prerelease** with tag `v0.8.0`, attach `dist/FolderTreePublisher-0.8.0.zip` and its `.sha256`, and include the 0.8.0 changelog plus tested Lightroom/OS versions.
6. Install the extracted release ZIP through Lightroom's Plug-in Manager and verify the version, About links, translations, and publication lifecycle before announcing it.

The workflow checks and builds artifacts; it does not automatically publish releases. A donation button can be added later through `.github/FUNDING.yml` after the owner supplies a valid supported funding account or URL.

## License

Source files use SPDX identifier `GPL-3.0-only`. LICENSE contains the unmodified GNU GPLv3 text. The archive includes the same license inside the installable plug-in folder. Keep it with copies of the plug-in and provide corresponding source as required by GPLv3.
