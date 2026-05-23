#!/usr/bin/env python3
"""Regenerate website/docs/tutorials/*.md from examples/<slug>/README.md.

Each tutorial in the Docusaurus site is a verbatim copy of the runnable
example's README, wrapped in Docusaurus frontmatter and a Claude-readable
MDX banner. This keeps a single source of truth (the example dir) and
avoids manual drift between docs and runnable code.

The previous version of this script wrote to docs/tutorials/ with an HTML
banner; that intermediate `docs/` tree was retired when the website
became the canonical published surface. The website's MDX 3 parser
chokes on HTML comments in `.md` files, so the banner is now `{/* */}`.

Usage
-----

    # regenerate
    python scripts/sync_tutorials.py

    # CI-friendly drift check: exit nonzero if regenerating would change
    # any committed tutorial file
    python scripts/sync_tutorials.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / 'examples'
TUTORIALS_DIR = REPO_ROOT / 'website' / 'docs' / 'tutorials'

BANNER_TEMPLATE = (
    '{{/* Auto-generated upstream from examples/{slug}/README.md by '
    'scripts/sync_tutorials.py. Edit the source README; do not edit '
    'this file directly. */}}\n\n'
)


def _example_dirs() -> list[Path]:
    """Return sorted example directories that contain a README.md."""
    return sorted(
        d for d in EXAMPLES_DIR.iterdir()
        if d.is_dir() and (d / 'README.md').exists()
    )


def _parse_h1_and_body(source: str) -> tuple[str, str]:
    """Split the source README into (title, body-after-h1).

    The source must begin with a level-1 heading (`# Title`); the body
    is everything after that line, with one trailing blank line skipped
    if present.
    """
    lines = source.split('\n')
    if not lines or not lines[0].startswith('# '):
        raise ValueError('Source README must begin with a level-1 heading')
    title = lines[0][2:].strip()
    rest = lines[1:]
    if rest and rest[0].strip() == '':
        rest = rest[1:]
    return title, '\n'.join(rest)


def _render(slug: str, source: str) -> str:
    """Wrap the source README in Docusaurus frontmatter + MDX banner."""
    title, body = _parse_h1_and_body(source)
    sidebar_position = int(slug.split('-', 1)[0])
    frontmatter = (
        '---\n'
        f'id: {slug}\n'
        f'title: "{title}"\n'
        f'sidebar_position: {sidebar_position}\n'
        '---\n\n'
    )
    h1 = f'# {title}\n\n'
    banner = BANNER_TEMPLATE.format(slug=slug)
    return frontmatter + h1 + banner + body


def regenerate() -> dict[str, str]:
    """Build the {tutorial filename: rendered content} mapping from sources."""
    out: dict[str, str] = {}
    for example_dir in _example_dirs():
        slug = example_dir.name
        source = (example_dir / 'README.md').read_text(encoding='utf-8')
        out[f'{slug}.md'] = _render(slug, source)
    return out


def write_all(content: dict[str, str]) -> None:
    """Write every tutorial file; create the tutorials dir if missing."""
    TUTORIALS_DIR.mkdir(parents=True, exist_ok=True)
    for name, body in content.items():
        (TUTORIALS_DIR / name).write_text(body, encoding='utf-8')


def check() -> int:
    """Compare regenerated content against committed files.

    Returns 0 if they match, 1 if they don't (mirrors a CI gate).
    """
    expected = regenerate()
    mismatches: list[str] = []
    for name, body in expected.items():
        path = TUTORIALS_DIR / name
        if not path.exists():
            mismatches.append(f'{name}: missing')
            continue
        on_disk = path.read_text(encoding='utf-8')
        if on_disk != body:
            mismatches.append(f'{name}: out of sync')

    # also flag files in tutorials/ that no longer correspond to an example.
    # `index.mdx` is the hand-maintained category landing; leave it alone.
    expected_names = set(expected) | {'index.mdx'}
    for path in TUTORIALS_DIR.glob('*.md'):
        if path.name not in expected_names:
            mismatches.append(f'{path.name}: orphan (no matching example)')

    if mismatches:
        print('website/docs/tutorials/ is out of sync with examples/:', file=sys.stderr)
        for m in mismatches:
            print(f'  - {m}', file=sys.stderr)
        print(
            '\nRegenerate with: python scripts/sync_tutorials.py',
            file=sys.stderr,
        )
        return 1
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--check', action='store_true',
        help='Exit nonzero if regenerated content would differ from disk.',
    )
    args = parser.parse_args(argv)

    if args.check:
        return check()
    write_all(regenerate())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
