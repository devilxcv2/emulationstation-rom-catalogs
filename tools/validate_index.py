#!/usr/bin/env python3
"""Check the committed index against catalog files without changing timestamps."""
import json
from pathlib import Path
from build_index import build

root = Path(__file__).resolve().parents[1]
committed = json.loads((root / 'index.json').read_text(encoding='utf-8'))
assert committed['schema_version'] == 1
assert committed['catalogs'], 'Empty catalog index'
first_url = committed['catalogs'][0]['url']
base_url = first_url.rsplit('/catalogs/', 1)[0]
actual = build(root, base_url, committed['updated_at'])
assert actual == committed, 'index.json differs from catalogs; run tools/build_index.py and commit the index'
print(f'Validated {len(actual["catalogs"])} catalogs and their SHA-256 checksums')
