#!/usr/bin/env python3
"""Build the versioned index consumed by EmulationStation's online catalogs menu."""
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

LABELS = {'3do': 'Panasonic 3DO', 'gb': 'Game Boy', 'gbc': 'Game Boy Color', 'gba': 'Game Boy Advance', 'nes': 'Nintendo Entertainment System', 'snes': 'Super Nintendo', 'psx': 'PlayStation', 'ps2': 'PlayStation 2', 'psp': 'PlayStation Portable', 'n64': 'Nintendo 64', 'nds': 'Nintendo DS', 'dreamcast': 'Dreamcast', 'megadrive': 'Mega Drive', 'mastersystem': 'Master System', 'gamegear': 'Game Gear', 'mame': 'MAME', 'fbneo': 'FinalBurn Neo'}


def build(root: Path, base_url: str, timestamp: str | None = None) -> dict:
    if not base_url.startswith('https://'):
        raise ValueError('base_url must use HTTPS')
    catalogs = []
    for path in sorted((root / 'catalogs').glob('*.jsonl')):
        system = path.stem.lower()
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', system):
            raise ValueError(f'Invalid system identifier: {system}')
        data = path.read_bytes()
        count = 0
        seen = set()
        for number, line in enumerate(data.decode('utf-8-sig').splitlines(), 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f'{path.name}:{number}: expected object')
            if item.get('type') == 'file':
                relative = item.get('p', '').replace('\\', '/')
                if not relative or relative.startswith('/') or any(part in ('', '.', '..') for part in relative.split('/')):
                    raise ValueError(f'{path.name}:{number}: unsafe game path')
                if any(isinstance(source, dict) and isinstance(source.get('u'), str) and source['u'].startswith(('https://', 'http://')) for source in item.get('urls', [])):
                    key = relative.lower()
                    if key not in seen:
                        count += 1
                        seen.add(key)
        digest = hashlib.sha256(data).hexdigest()
        catalogs.append({'system': system, 'title': LABELS.get(system, system.replace('_', ' ').replace('-', ' ').title()), 'url': f'{base_url.rstrip("/")}/catalogs/{path.name}', 'version': digest[:16], 'game_count': count, 'download_bytes': len(data), 'sha256': digest})
    if not catalogs:
        raise ValueError('No JSONL catalogs found')
    now = timestamp or dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    return {'schema_version': 1, 'name': 'EmulationStation ROM Catalogs', 'updated_at': now, 'catalogs': catalogs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--base-url', default='https://raw.githubusercontent.com/devilxcv2/emulationstation-rom-catalogs/main')
    args = parser.parse_args()
    index = build(args.root, args.base_url)
    output = args.root / 'index.json'
    if output.is_file():
        old = json.loads(output.read_text(encoding='utf-8'))
        if old.get('catalogs') == index['catalogs'] and old.get('schema_version') == index['schema_version']:
            index['updated_at'] = old['updated_at']
    temporary = output.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(output)
    print(f'{len(index["catalogs"])} catalogs, {sum(c["game_count"] for c in index["catalogs"]):,} games, {sum(c["download_bytes"] for c in index["catalogs"]):,} bytes')


if __name__ == '__main__':
    main()
