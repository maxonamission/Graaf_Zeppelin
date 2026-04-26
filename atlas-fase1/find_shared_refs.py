#!/usr/bin/env python3
"""Vind gedeelde literatuur-referenties tussen twee model-registers.

Hybride benadering: dit script telt exacte ref_id-matches en fuzzy
kandidaten (zelfde eerste-auteur-familienaam + jaar, andere ref_id) en
schrijft een leesbaar markdown-rapport voor handmatige review van de
mismatches en uniek-per-model steekproef.

Gebruik:
    python find_shared_refs.py --from L2 D1 --out fase1-meting.md
    python find_shared_refs.py --from L2 D1            # alleen tellingen

Default: vergelijkt L2 ↔ D1 (zelfde meso-niveau, meest directe overlap).
Werkt op elk modelpaar dat een gestructureerd JSON-register heeft.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

DEFAULT_FROM = ["L2", "D1"]
SAMPLE_SIZE = 10  # uniek-per-model steekproef in rapport


def load_paths(config_path: Path) -> dict:
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def load_register(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_name(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_form = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_form.lower().strip()


def first_author_family(entry: dict) -> str | None:
    authors = entry.get("authors", [])
    if not authors:
        return None
    first = authors[0]
    if isinstance(first, dict):
        return first.get("family")
    if isinstance(first, str):
        return first
    return None


def fuzzy_key(entry: dict) -> tuple[str, int] | None:
    family = first_author_family(entry)
    year = entry.get("year")
    if family is None or year is None:
        return None
    try:
        return (normalize_name(family), int(year))
    except (TypeError, ValueError):
        return None


def index_by_ref_id(entries: list[dict]) -> dict[str, dict]:
    return {e["ref_id"]: e for e in entries if "ref_id" in e}


def index_by_fuzzy(entries: list[dict]) -> dict[tuple[str, int], list[dict]]:
    out: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for e in entries:
        key = fuzzy_key(e)
        if key:
            out[key].append(e)
    return out


def short_title(entry: dict, max_len: int = 80) -> str:
    title = entry.get("title", "(geen titel)")
    return title if len(title) <= max_len else title[: max_len - 1] + "…"


def author_year_label(entry: dict) -> str:
    family = first_author_family(entry) or "?"
    year = entry.get("year", "?")
    return f"{family} {year}"


def render_report(model_a: str, model_b: str, results: dict) -> str:
    lines = [
        f"# Cross-model literatuur-analyse — {model_a} ↔ {model_b}",
        "",
        "## Tellingen",
        "",
        f"- Entries in **{model_a}**: {results['count_a']}",
        f"- Entries in **{model_b}**: {results['count_b']}",
        f"- Exacte `ref_id`-matches: **{len(results['exact'])}**",
        f"- Fuzzy kandidaten (zelfde auteur+jaar, andere `ref_id`): **{len(results['fuzzy'])}**",
        f"- Uniek in {model_a}: **{len(results['unique_a'])}**",
        f"- Uniek in {model_b}: **{len(results['unique_b'])}**",
        "",
        "## Exacte matches",
        "",
    ]
    if not results["exact"]:
        lines.append("(geen)")
    else:
        lines.append("| ref_id | titel |")
        lines.append("|---|---|")
        for ref_id, entry in sorted(results["exact"].items()):
            lines.append(f"| `{ref_id}` | {short_title(entry)} |")

    lines.extend(["", "## Fuzzy kandidaten", ""])
    if not results["fuzzy"]:
        lines.append("(geen)")
    else:
        lines.append(
            f"| {model_a} `ref_id` | {model_b} `ref_id` | auteur+jaar | "
            f"titel ({model_a}) | titel ({model_b}) |"
        )
        lines.append("|---|---|---|---|---|")
        for pair in results["fuzzy"]:
            ref_a = pair["a"].get("ref_id", "?")
            ref_b = pair["b"].get("ref_id", "?")
            ay = author_year_label(pair["a"])
            lines.append(
                f"| `{ref_a}` | `{ref_b}` | {ay} | "
                f"{short_title(pair['a'])} | {short_title(pair['b'])} |"
            )

    for label, entries in [
        (f"Steekproef uniek in {model_a} (eerste {SAMPLE_SIZE})", results["unique_a"]),
        (f"Steekproef uniek in {model_b} (eerste {SAMPLE_SIZE})", results["unique_b"]),
    ]:
        lines.extend(["", f"## {label}", ""])
        sample = sorted(entries.values(), key=lambda e: e.get("ref_id", ""))[:SAMPLE_SIZE]
        if not sample:
            lines.append("(geen)")
            continue
        lines.append("| ref_id | titel |")
        lines.append("|---|---|")
        for entry in sample:
            lines.append(f"| `{entry.get('ref_id', '?')}` | {short_title(entry)} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Hoe te lezen",
            "",
            "- **Exacte matches** zijn directe promotie-kandidaten (via `promote_reference.py`).",
            "- **Fuzzy kandidaten** vragen handmatige beoordeling: zelfde bron "
            "met andere `ref_id`-conventie? Of toevallig dezelfde auteur in "
            "hetzelfde jaar voor verschillende werken?",
            "- **Uniek-per-model steekproef** geeft een gevoel van waar de "
            "registers van elkaar verschillen — bewust of door ontbrekende "
            "cross-referencing.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vind gedeelde refs tussen twee model-registers.",
    )
    parser.add_argument(
        "--from",
        dest="models",
        nargs=2,
        default=DEFAULT_FROM,
        metavar=("MODEL_A", "MODEL_B"),
        help=f"Twee modelprefixen (default: {DEFAULT_FROM[0]} {DEFAULT_FROM[1]})",
    )
    parser.add_argument("--config", default="_scripts/paths.yml")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--out",
        default=None,
        help="Pad voor markdown-rapport (default: alleen tellingen naar stdout)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    if not config_path.exists():
        print(f"ERROR: config niet gevonden: {config_path}", file=sys.stderr)
        return 1

    paths = load_paths(config_path)
    model_a, model_b = args.models

    paths_models = paths.get("models", {})
    for m in (model_a, model_b):
        if m not in paths_models:
            print(f"ERROR: model '{m}' niet in paths.yml", file=sys.stderr)
            return 1

    path_a = repo_root / paths_models[model_a]
    path_b = repo_root / paths_models[model_b]
    for p, m in ((path_a, model_a), (path_b, model_b)):
        if not p.exists():
            print(f"ERROR: register voor {m} niet gevonden: {p}", file=sys.stderr)
            return 1

    entries_a = load_register(path_a).get("references", [])
    entries_b = load_register(path_b).get("references", [])

    by_id_a = index_by_ref_id(entries_a)
    by_id_b = index_by_ref_id(entries_b)
    common_ids = set(by_id_a) & set(by_id_b)
    exact = {ref_id: by_id_a[ref_id] for ref_id in common_ids}

    by_fuzzy_a = index_by_fuzzy(entries_a)
    by_fuzzy_b = index_by_fuzzy(entries_b)
    fuzzy_pairs: list[dict] = []
    for key, entries in by_fuzzy_a.items():
        if key in by_fuzzy_b:
            for ea in entries:
                for eb in by_fuzzy_b[key]:
                    if ea.get("ref_id") != eb.get("ref_id"):
                        fuzzy_pairs.append({"a": ea, "b": eb})

    unique_a_ids = set(by_id_a) - set(by_id_b)
    unique_b_ids = set(by_id_b) - set(by_id_a)
    unique_a = {rid: by_id_a[rid] for rid in unique_a_ids}
    unique_b = {rid: by_id_b[rid] for rid in unique_b_ids}

    results = {
        "count_a": len(entries_a),
        "count_b": len(entries_b),
        "exact": exact,
        "fuzzy": fuzzy_pairs,
        "unique_a": unique_a,
        "unique_b": unique_b,
    }

    print(f"=== {model_a} ↔ {model_b} ===")
    print(f"  {model_a}: {results['count_a']} entries")
    print(f"  {model_b}: {results['count_b']} entries")
    print(f"  exacte ref_id-matches: {len(exact)}")
    print(f"  fuzzy kandidaten (auteur+jaar, andere ref_id): {len(fuzzy_pairs)}")
    print(f"  uniek in {model_a}: {len(unique_a)}")
    print(f"  uniek in {model_b}: {len(unique_b)}")

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.write_text(render_report(model_a, model_b, results), encoding="utf-8")
        print(f"  rapport: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
