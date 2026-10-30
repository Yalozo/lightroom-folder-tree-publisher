# Copyright (C) 2026 Yalozo Andrey
# SPDX-License-Identifier: GPL-3.0-only

"""Build a reproducible installable archive; never upload or publish anything."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'FolderTreePublisher.lrplugin'
info = (PLUGIN / 'Info.lua').read_text()
version_match = re.search(r'major\s*=\s*(\d+),\s*minor\s*=\s*(\d+),\s*revision\s*=\s*(\d+)', info)
assert version_match, 'Missing version in Info.lua'
version = '.'.join(version_match.groups())
docs = ['README.md', 'README.ru.md', 'TRANSLATING.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE']
for name in docs:
    if not (ROOT / name).is_file():
        raise SystemExit(f'Release is not ready: missing {name}')
files = [(p, p.relative_to(ROOT).as_posix()) for p in sorted(PLUGIN.iterdir())
         if p.suffix in {'.lua', '.png', '.svg', '.txt'}]
files += [(ROOT / name, name) for name in docs]
files += [(p, p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / 'docs').glob('USER_GUIDE*.md'))]
files += [(p, p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / 'docs/screenshots').glob('*.png')) if re.fullmatch(r'0[1-8]-[a-z-]+[.]png', p.name) and not p.stem.endswith('-edited')]
# Keep the license with the installed plug-in too.
files.append((ROOT / 'LICENSE', 'FolderTreePublisher.lrplugin/LICENSE.txt'))
out = ROOT / 'dist'
out.mkdir(exist_ok=True)
archive = out / f'FolderTreePublisher-{version}.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for path, name in sorted(files, key=lambda pair: pair[1]):
        entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.create_system = 3
        entry.external_attr = 0o100644 << 16
        z.writestr(entry, path.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.sha256').write_text(f'{checksum}  {archive.name}\n')
print(f'Built {archive.name}\nSHA-256: {checksum}')
