#!/usr/bin/env python3

import re
import sys
from pathlib import Path


def normalize_text(text: str) -> str:
    text = text.replace("\\~~", "~~")
    text = re.sub(r"<br/>\s*&#x20;\|", "<br/> |", text)

    lines = text.splitlines()
    out = []
    in_table = False
    table_header_seen = False

    for line in lines:
        stripped = line.lstrip()
        is_table_row = stripped.startswith("|")

        if is_table_row:
            out.append(line)
            if in_table:
                continue
            in_table = True
            table_header_seen = False
            continue

        if in_table:
            if stripped == "":
                in_table = False
                table_header_seen = False
                out.append(line)
                continue

            # The second pipe-led line is usually the separator row.
            if len(out) >= 2 and out[-1].lstrip().startswith("|") and not table_header_seen:
                table_header_seen = True

            if out and out[-1].lstrip().startswith("|"):
                out[-1] = out[-1] + "<br/>" + stripped
                continue

            in_table = False
            table_header_seen = False

        out.append(line)

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def process_file(path: Path) -> bool:
    original = path.read_text()
    updated = normalize_text(original)
    if updated == original:
        return False
    path.write_text(updated)
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: normalize_exported_markdown.py <file-or-dir> [<file-or-dir> ...]", file=sys.stderr)
        return 1

    changed = 0
    for raw in sys.argv[1:]:
        path = Path(raw).resolve()
        if path.is_dir():
            for md in path.rglob("*.md"):
                changed += int(process_file(md))
        elif path.suffix.lower() == ".md" and path.is_file():
            changed += int(process_file(path))

    print(f"normalized {changed} markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
