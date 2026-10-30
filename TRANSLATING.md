# Translating Folder Tree Publisher

The plug-in uses Lightroom SDK's native `LOC` / ZString localization. No Lua changes are needed to add a translation.

1. Copy `FolderTreePublisher.lrplugin/TranslatedStrings_en.txt` to `TranslatedStrings_XX.txt` in the same folder as `Info.lua`. Replace `XX` with Lightroom's language code, for example `de` or `fr`.
2. Translate only the text **after the first `=`** on each line. Keep every key on the left unchanged.
3. Save as plain UTF-8 text. Each entry must remain on one line, enclosed in double quotes. Do not add comments or trailing commas.
4. Keep `^n` (line breaks), numbered placeholders such as `^1`, and formatting tokens such as `%d` intact. A few messages end with a space before a filename is appended: keep that space. Do not translate the product name Folder Tree Publisher.
5. Install/reload the plug-in and restart Lightroom with the corresponding interface language. Check the Plug-in Manager, service settings, collection settings, preview, and error dialogs.
6. Submit the new file with your translation. Mention the Lightroom version and operating system used to check the layout.

Example:

```text
"$$$/FolderTreePublisher/PublishFolder=Publication folder"
"$$$/FolderTreePublisher/PublishFolder=Папка публикации"
```

These example lines belong in separate language files, not together in one file. New translations should have the same keys as the English file. Use `^[` and `^]` for double quotes inside a value rather than literal double quotes. The dictionaries are text resources, not Lua scripts or JSON.

Lightroom chooses the dictionary according to its own UI language. Missing languages or entries fall back to the English text embedded in the Lua code. This does not add a language selector or support for additional Lightroom UI languages.

Localization changes labels and messages only. Existing collection names and all user-entered paths remain unchanged; only newly created default collections receive a localized default name. The example path shown in the collection dialog is translated, but it is illustrative and is never used to calculate real output paths. Lightroom and operating-system errors are displayed in the language supplied by those systems.

For maintainers: `python3 tests/test_localization.py` validates the included English/Russian dictionaries against Lua call sites. Run the functional tests with `PLUGIN_TEST_LANGUAGE=ru`, `en`, and a missing language such as `de` (requires Lupa). These tests emulate `LOC`; visual verification and native dictionary loading must also be checked in Lightroom.

## Для переводчиков на русский

Изменяйте только значения справа от первого `=` в `TranslatedStrings_ru.txt`, сохраняя ключи, кавычки, `^n`, `^1` и `%d`. Файл сохраняется в UTF-8. Для проверки выберите русский язык интерфейса Lightroom и перезапустите приложение. Новые переводы не меняют названия существующих коллекций или пути файлов.
