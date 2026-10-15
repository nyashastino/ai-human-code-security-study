"""Fetch pinned first-party scan inputs locally; verify every file's SHA-256.

Downloaded files are gitignored. Consult licences/ before redistributing them.
"""
import csv
import hashlib
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def main():
    with (ROOT/'data/human-files.csv').open() as f:
        records = list(csv.DictReader(f))
    for row in records:
        dest = ROOT/'data/human-local'/row['scan_path']
        if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == row['sha256']:
            continue
        url = f"https://raw.githubusercontent.com/{row['repository']}/{row['commit']}/{quote(row['repository_path'], safe='/')}"
        with urlopen(Request(url, headers={'User-Agent':'code-security-reproduction'}), timeout=60) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != row['sha256']:
            raise ValueError('Source hash mismatch: '+row['scan_path'])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    print(f'Verified {len(records)} local human source files; excluded from Git.')

if __name__ == '__main__':
    main()
