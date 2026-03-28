#!/usr/bin/env python3

import json
import os
import re
import sys
from pathlib import Path


LINK_RE = re.compile(
    r"(?P<prefix>\()"
    r"(?P<url>https://www\.yuque\.com/(?P<abs_ns>[^)\s]+/[^)\s]+)/(?P<abs_key>[^)#?\s]+)(?:[?#][^)]*)?"
    r"|/(?P<rel_ns>[^)\s]+/[^)\s]+)/(?P<rel_key>[^)#?\s]+)(?:[?#][^)]*)?)"
    r"(?P<suffix>\))"
)
URL_RE = re.compile(r"^url:\s+https://www\.yuque\.com/(?P<namespace>[^/\s]+/[^/\s]+)/(?P<key>[^\s]+)\s*$")


def load_namespace_meta(vault: Path):
    meta_dirs = list((vault / ".meta").glob("*/*"))
    if not meta_dirs:
        raise SystemExit(f"missing .meta data under {vault}")

    namespace_to_id_to_slug = {}
    for meta_dir in meta_dirs:
        docs = json.loads((meta_dir / "docs.json").read_text())
        namespace = f"{meta_dir.parent.name}/{meta_dir.name}"
        namespace_to_id_to_slug[namespace] = {str(doc["id"]): doc["slug"] for doc in docs}
    return namespace_to_id_to_slug


def build_slug_to_path(vault: Path):
    namespace_to_slug_to_path = {}
    for md_path in vault.rglob("*.md"):
        rel_path = md_path.relative_to(vault).as_posix()
        for line in md_path.read_text().splitlines():
            match = URL_RE.match(line.strip())
            if not match:
                continue
            namespace = match.group("namespace")
            namespace_to_slug_to_path.setdefault(namespace, {})[match.group("key")] = rel_path
            break
    return namespace_to_slug_to_path


def rewrite_file(md_path: Path, vault: Path, key_to_path_by_namespace: dict[str, dict[str, str]]):
    original = md_path.read_text()
    replacements = 0

    def replace(match: re.Match[str]):
        nonlocal replacements
        target_namespace = match.group("abs_ns") or match.group("rel_ns")
        key_to_path = key_to_path_by_namespace.get(target_namespace)
        if not key_to_path:
            return match.group(0)

        key = match.group("abs_key") or match.group("rel_key")
        target_path = key_to_path.get(key)
        if not target_path:
            return match.group(0)

        relative_path = os.path.relpath(vault / target_path, start=md_path.parent).replace("\\", "/")
        replacements += 1
        return f"{match.group('prefix')}{relative_path}{match.group('suffix')}"

    updated = LINK_RE.sub(replace, original)
    if updated != original:
        md_path.write_text(updated)

    return replacements


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: fix_yuque_obsidian_links.py <vault-path> [<vault-path> ...]")

    for raw_vault in sys.argv[1:]:
        vault = Path(raw_vault).resolve()
        namespace_to_id_to_slug = load_namespace_meta(vault)
        namespace_to_slug_to_path = build_slug_to_path(vault)

        key_to_path_by_namespace = {}
        for namespace, id_to_slug in namespace_to_id_to_slug.items():
            slug_to_path = namespace_to_slug_to_path.get(namespace, {})
            key_to_path = dict(slug_to_path)
            for doc_id, slug in id_to_slug.items():
                if slug in slug_to_path:
                    key_to_path[doc_id] = slug_to_path[slug]
            key_to_path_by_namespace[namespace] = key_to_path

        total = 0
        for md_path in vault.rglob("*.md"):
            total += rewrite_file(md_path, vault, key_to_path_by_namespace)

        print(f"{vault}: replaced {total} links")


if __name__ == "__main__":
    main()
