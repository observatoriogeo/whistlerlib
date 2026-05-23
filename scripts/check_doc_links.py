#!/usr/bin/env python3
"""Verify every relative link in docs/ resolves to a real file on disk.

Walks `docs/**/*.md`, extracts inline markdown links `[text](path)` and
HTML `<img src="path">`, ignores anything starting with `http://`,
`https://`, `mailto:`, or `#`, and resolves the remainder against the
markdown file's parent directory. Exits nonzero on the first broken link.

Usage:

    python scripts/check_doc_links.py            # check docs/
    python scripts/check_doc_links.py path/to/   # check a different root
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent

# Markdown inline link: [text](href), non-greedy on text, allows href to
# contain anything but ')' and whitespace. Fragments and queries stripped
# at check time.
MD_LINK_RE = re.compile(r'\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')

# HTML <img src="...">, keep simple, only matches double quotes.
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)


def _extract_targets(text: str) -> list[str]:
    return MD_LINK_RE.findall(text) + IMG_SRC_RE.findall(text)


def _is_external(target: str) -> bool:
    scheme = urlsplit(target).scheme
    if scheme:
        return True
    if target.startswith('#') or target.startswith('mailto:'):
        return True
    return False


def _strip_anchor(target: str) -> str:
    # 'foo.md#heading' -> 'foo.md'
    return unquote(urlsplit(target)._replace(fragment='', query='').geturl())


def check(docs_root: Path) -> list[str]:
    broken: list[str] = []
    md_files = sorted(docs_root.rglob('*.md'))
    for md in md_files:
        text = md.read_text(encoding='utf-8')
        for raw in _extract_targets(text):
            if _is_external(raw):
                continue
            target = _strip_anchor(raw)
            if not target:
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                broken.append(
                    f'{md.relative_to(REPO_ROOT)} -> {raw} '
                    f'(resolved to {resolved})'
                )
    return broken


def main(argv: list[str]) -> int:
    root = Path(argv[0]).resolve() if argv else REPO_ROOT / 'docs'
    if not root.exists():
        print(f'no such directory: {root}', file=sys.stderr)
        return 2
    broken = check(root)
    if broken:
        print(f'{len(broken)} broken link(s):', file=sys.stderr)
        for b in broken:
            print(f'  - {b}', file=sys.stderr)
        return 1
    print(f'OK, all relative links in {root.relative_to(REPO_ROOT)} resolve.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
