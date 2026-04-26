#!/usr/bin/env python3
"""Promoveer literatuur-referenties naar het gedeelde register.

Volgens governance in A_/literatuur/README.md: bron-toevoeging gebeurt
door de bouwer van het tweede betrokken model. Dit script automatiseert
de mechaniek (transformatie, validatie, lokale shared-markering en
update van metadata).

Gebruik:
    python promote_reference.py REF_Edmondson_1999 --from L2 D1
    python promote_reference.py REF_Edmondson_1999 --from L2 D1 \\
        --concepts psychological-safety team-learning
    python promote_reference.py REF_Edmondson_1999 --from L2 D1 --dry-run

Het script doet geen overlap-detectie tussen modellen — dat is Fase 1.
Het matcht ook niet fuzzy: alleen exacte ref_id-vergelijking.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

REF_ID_PATTERN = re.compile(r"^REF_[A-Z][A-Za-z\-]*_\d{4}[a-z]?$")

DEFAULT_STRIP_FIELDS = {"avv_usage", "sdm_usage", "thema_codes", "shared"}


def load_paths(config_path: Path) -> dict:
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def load_register(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_register(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def find_ref(register: dict, ref_id: str) -> dict | None:
    for entry in register.get("references", []):
        if entry.get("ref_id") == ref_id:
            return entry
    return None


def validate_ref_id(ref_id: str) -> tuple[bool, str | None]:
    if not REF_ID_PATTERN.match(ref_id):
        return False, (
            f"ref_id moet voldoen aan REF_<Author>_<Year> (bv. REF_Edmondson_1999): {ref_id}"
        )
    return True, None


def transform_to_shared(
    local_entry: dict, used_by: list[str], concepts: list[str], strip_fields: set[str]
) -> dict:
    shared = {k: v for k, v in local_entry.items() if k not in strip_fields}
    shared["used_by"] = list(used_by)
    if concepts:
        shared["concepts"] = list(concepts)
    return shared


def collect_source_entries(
    ref_id: str, source_models: list[str], paths: dict, repo_root: Path
) -> tuple[dict | None, list[str], list[str]]:
    """Returnt (eerste-gevonden-entry, modellen-met-entry, waarschuwingen)."""
    source_entry = None
    found_in: list[str] = []
    warnings: list[str] = []

    for model in source_models:
        if model not in paths["models"]:
            warnings.append(f"onbekend model '{model}' in paths.yml — skipping")
            continue
        local_path = repo_root / paths["models"][model]
        if not local_path.exists():
            warnings.append(f"register voor {model} niet gevonden ({local_path}) — skipping")
            continue
        local_register = load_register(local_path)
        entry = find_ref(local_register, ref_id)
        if entry:
            if source_entry is None:
                source_entry = entry
            found_in.append(model)

    return source_entry, found_in, warnings


def mark_local_shared(ref_id: str, models: list[str], paths: dict, repo_root: Path) -> int:
    count = 0
    for model in models:
        local_path = repo_root / paths["models"][model]
        local_register = load_register(local_path)
        for entry in local_register.get("references", []):
            if entry.get("ref_id") == ref_id:
                entry["shared"] = True
                count += 1
        save_register(local_path, local_register)
    return count


def update_metadata(gedeeld: dict, ref_id: str, used_by: list[str]) -> None:
    meta = gedeeld.setdefault("metadata", {})
    meta["total_references"] = len(gedeeld.get("references", []))
    meta["date"] = str(date.today())
    change_log = meta.setdefault("change_log", [])
    change_log.append(
        {
            "version": meta.get("version", "0.0") + "-promote",
            "date": str(date.today()),
            "change": f"Promotie {ref_id} (used_by: {used_by})",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promoveer een ref_id naar het gedeelde register.",
    )
    parser.add_argument("ref_id", help="bv. REF_Edmondson_1999")
    parser.add_argument(
        "--from",
        dest="source_models",
        required=True,
        nargs="+",
        help="Modelprefix(en) waar de bron uit komt (L1, L2, L3, D1, C1)",
    )
    parser.add_argument(
        "--concepts",
        nargs="*",
        default=[],
        help="Architecturele concepten (optioneel)",
    )
    parser.add_argument(
        "--config",
        default="_scripts/paths.yml",
        help="paths-config (default: _scripts/paths.yml)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Atlas-repo root (default: huidige map)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon wat zou gebeuren zonder te schrijven",
    )
    args = parser.parse_args()

    ok, msg = validate_ref_id(args.ref_id)
    if not ok:
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    repo_root = Path(args.repo_root).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    if not config_path.exists():
        print(f"ERROR: config niet gevonden: {config_path}", file=sys.stderr)
        return 1

    paths = load_paths(config_path)
    strip_fields = set(paths.get("strip_on_promote", DEFAULT_STRIP_FIELDS))

    gedeeld_path = repo_root / paths["gedeeld"]
    if not gedeeld_path.exists():
        print(f"ERROR: gedeeld register niet gevonden: {gedeeld_path}", file=sys.stderr)
        return 1
    gedeeld = load_register(gedeeld_path)

    if find_ref(gedeeld, args.ref_id):
        print(
            f"ERROR: {args.ref_id} bestaat al in gedeeld register",
            file=sys.stderr,
        )
        return 1

    source_entry, found_in, warnings = collect_source_entries(
        args.ref_id, args.source_models, paths, repo_root
    )
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if not source_entry:
        print(
            f"ERROR: {args.ref_id} niet gevonden in opgegeven modellen "
            f"({', '.join(args.source_models)})",
            file=sys.stderr,
        )
        return 1

    if len(found_in) < 2 and "A_" not in args.source_models:
        print(
            f"WARNING: {args.ref_id} gevonden in slechts {len(found_in)} model(len). "
            f"Governance: promotie hoort vanaf 2 modellen — verifieer.",
            file=sys.stderr,
        )

    shared_entry = transform_to_shared(source_entry, found_in, args.concepts, strip_fields)

    if args.dry_run:
        print("=== DRY-RUN: zou opnemen ===")
        print(json.dumps(shared_entry, indent=2, ensure_ascii=False))
        print(f"\n=== zou markeren shared: true in: {', '.join(found_in)} ===")
        return 0

    gedeeld.setdefault("references", []).append(shared_entry)
    update_metadata(gedeeld, args.ref_id, found_in)
    save_register(gedeeld_path, gedeeld)

    marked = mark_local_shared(args.ref_id, found_in, paths, repo_root)

    print(f"OK: {args.ref_id} gepromoveerd (used_by: {', '.join(found_in)})")
    print(f"  gedeeld register: {gedeeld_path.relative_to(repo_root)}")
    print(f"  lokale entries gemarkeerd shared=true: {marked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
