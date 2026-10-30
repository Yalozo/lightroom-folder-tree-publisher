# Copyright (C) 2026 Yalozo Andrey
# SPDX-License-Identifier: GPL-3.0-only

"""Validate Lightroom ZString dictionaries and all localizable call sites."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'FolderTreePublisher.lrplugin'
source = '\n'.join(p.read_text() for p in PLUGIN.glob('*.lua'))
references = {}
for key, fallback in re.findall(r'LOC\("(\$\$\$/FolderTreePublisher/[^=]+)=([^"\n]*)"', source):
    assert key.isascii() and fallback.isascii(), key
    assert key not in references or references[key] == fallback, key
    references[key] = fallback
assert references
assert not re.search('[А-Яа-яЁё]', source), 'Unlocalized Russian text in Lua'
for language in ('en', 'ru'):
    entries = {}
    for line in (PLUGIN / f'TranslatedStrings_{language}.txt').read_text(encoding='utf-8-sig').splitlines():
        match = re.fullmatch(r'"(\$\$\$/FolderTreePublisher/[A-Za-z0-9/]+)=([^"\n]+)"', line)
        assert match, line
        key, text = match.groups()
        assert key not in entries, key
        entries[key] = text
    assert entries.keys() == references.keys(), (language, entries.keys() ^ references.keys())
    for key, fallback in references.items():
        assert sorted(re.findall(r'\^[1-9]', entries[key])) == sorted(re.findall(r'\^[1-9]', fallback)), key
        assert re.findall(r'%[a-z]', entries[key]) == re.findall(r'%[a-z]', fallback), key
        assert entries[key].count('^n') == fallback.count('^n'), key
        if language == 'en': assert entries[key] == fallback, key
print(f'PASS: {len(references)} keys, complete RU/EN dictionaries, placeholders and English fallbacks')
