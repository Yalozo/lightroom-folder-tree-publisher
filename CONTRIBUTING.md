# Contributing

Bug reports, translations, and focused pull requests are welcome. English and Russian are both welcome in discussions and issues.

## Development

The runtime is Lua supplied by Lightroom Classic. Python is needed only for development checks and packaging.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tests/test_localization.py
PLUGIN_TEST_LANGUAGE=ru python tests/test_plugin.py
PLUGIN_TEST_LANGUAGE=en python tests/test_plugin.py
PLUGIN_TEST_LANGUAGE=de python tests/test_plugin.py
python tools/build_release.py
```

Tests execute the Lua 5.1 code with mocked Lightroom APIs and a real temporary filesystem. They do not run Lightroom or transcode actual video. State explicitly whether you tested a change in Lightroom, including app and OS versions.

Use a separate destination folder and a small collection for manual checks. Verify first publish, republish, changes to collection paths, shared photos in two collections, removal, and video when affected. Never use important originals as an output folder.

## Project layout

- `FolderTreePublisher.lrplugin/`: installable source and resources.
- `tests/`: functional and localization checks.
- `tools/build_release.py`: versioned ZIP and SHA-256 checksum.
- `tools/build_icons.py`: reproducible geometric icon renderer.
- `TRANSLATING.md`: adding or updating language dictionaries.

Keep persistent setting keys and `LrToolkitIdentifier` stable. Existing catalogs depend on them. Add regression tests for changes to path safety, file replacement, or deletion. Keep Russian and English dictionaries in sync; localize user-facing text with `LOC`.

Do not commit generated ZIP archives, personal Lightroom catalogs, credentials, or personal photographs. Propose changes through a pull request with a concrete problem statement and validation results.

## License

Contributions are accepted under GPL-3.0-only, the project's license. Only submit code and assets you have the right to contribute under these terms. Preserve copyright notices and identify third-party components and their licenses.
