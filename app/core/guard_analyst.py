"""Guard Analyst — Post-hoc analyse van LLM Guard audit logs.

Analyseert geblokkeerde en doorgelaten queries om:
1. Nieuwe injectiepatronen te ontdekken (via LLM-classificatie)
2. False positives te identificeren
3. Concrete patronen voor te stellen voor de JSON-patronenlijst

Gebruik via CLI:
    python -m app.core.guard_analyst --help
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

# Audit log event types die relevant zijn voor analyse.
_RELEVANT_EVENTS = {"prompt_injection_blocked", "prompt_leakage_blocked"}

# ── Log parsing ──────────────────────────────────────────────────────────


def parse_audit_logs(log_lines: list[str]) -> list[dict[str, Any]]:
    """Parse structured JSON audit log lines.

    Returns a list of parsed log entries, filtering for guard-related events.
    """
    entries: list[dict[str, Any]] = []
    for line in log_lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = entry.get("event", "")
        if event in _RELEVANT_EVENTS:
            entries.append(entry)
    return entries


def summarize_blocked(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize blocked attempts from parsed audit log entries.

    Returns statistics useful for pattern review.
    """
    by_event: dict[str, int] = {}
    by_matched: dict[str, int] = {}
    by_user: dict[str, int] = {}

    for entry in entries:
        event = entry.get("event", "unknown")
        by_event[event] = by_event.get(event, 0) + 1

        matched = entry.get("extra", {}).get("matched", "unknown")
        by_matched[matched] = by_matched.get(matched, 0) + 1

        user_id = str(entry.get("user_id", "unknown"))
        by_user[user_id] = by_user.get(user_id, 0) + 1

    return {
        "total_blocked": len(entries),
        "by_event": dict(sorted(by_event.items(), key=lambda x: x[1], reverse=True)),
        "by_pattern_matched": dict(sorted(by_matched.items(), key=lambda x: x[1], reverse=True)),
        "by_user": dict(sorted(by_user.items(), key=lambda x: x[1], reverse=True)),
        "unique_users": len(by_user),
    }


# ── LLM-based analysis ──────────────────────────────────────────────────

_ANALYSIS_PROMPT = """Je bent een beveiligingsanalist. Analyseer de volgende geblokkeerde
gebruikersinvoer uit een causale redeneer-applicatie. Voor elk item:

1. Beoordeel of de blokkade terecht was (true positive) of onterecht (false positive)
2. Als het een true positive is: stel een nieuw regex-patroon voor dat dit en vergelijkbare
   varianten zou vangen
3. Als het een false positive is: leg uit waarom de gebruiker waarschijnlijk geen kwaad bedoelde

Geef je antwoord als JSON array met objecten:
```json
[
  {{
    "input": "de geblokkeerde invoer",
    "verdict": "true_positive" of "false_positive",
    "reasoning": "korte uitleg",
    "suggested_pattern": "regex patroon (alleen bij true_positive, anders null)",
    "category": "injection_override|persona_hijack|jailbreak|prompt_extraction|false_positive",
    "lang": "nl" of "en",
    "severity": "high|medium|low"
  }}
]
```

Geblokkeerde invoer:

{blocked_inputs}
"""


def build_analysis_prompt(entries: list[dict[str, Any]], max_items: int = 50) -> str:
    """Build an LLM prompt to analyse blocked inputs.

    Returns a prompt string ready for an LLM API call.
    """
    # Extract unique matched strings (deduplicate)
    seen: set[str] = set()
    items: list[str] = []
    for entry in entries[:max_items]:
        matched = entry.get("extra", {}).get("matched", "")
        if matched and matched not in seen:
            seen.add(matched)
            items.append(f'- "{matched}"')

    if not items:
        return ""

    blocked_inputs = "\n".join(items)
    return _ANALYSIS_PROMPT.format(blocked_inputs=blocked_inputs)


def parse_analysis_response(response_text: str) -> list[dict[str, Any]]:
    """Parse the LLM analysis response and extract suggested patterns.

    Returns a list of analysis results.  Robust against markdown code fences.
    """
    # Strip markdown code fences if present
    text = response_text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)

    try:
        results = json.loads(text)
        if isinstance(results, list):
            return results
    except json.JSONDecodeError:
        _logger.warning("Kon LLM-analyseresponse niet parsen als JSON")
    return []


def extract_new_patterns(
    analysis: list[dict[str, Any]],
    existing_patterns_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Extract suggested new patterns that aren't already in the patterns file.

    Returns pattern objects ready to be appended to the JSON file.
    """
    from app.core.llm_guard import _DEFAULT_PATTERNS_PATH

    path = existing_patterns_path or _DEFAULT_PATTERNS_PATH

    # Load existing patterns
    existing_regexes: set[str] = set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for p in data.get("injection_patterns", []):
            existing_regexes.add(p["pattern"])
        for p in data.get("leakage_patterns", []):
            existing_regexes.add(p["pattern"])
    except Exception:
        pass

    new_patterns: list[dict[str, Any]] = []
    for item in analysis:
        if item.get("verdict") != "true_positive":
            continue
        suggested = item.get("suggested_pattern")
        if not suggested or suggested in existing_regexes:
            continue
        # Validate the regex compiles
        try:
            re.compile(suggested, re.IGNORECASE)
        except re.error:
            _logger.warning("Voorgesteld patroon compileert niet: %r", suggested)
            continue
        new_patterns.append(
            {
                "pattern": suggested,
                "category": item.get("category", "unknown"),
                "lang": item.get("lang", "en"),
                "severity": item.get("severity", "medium"),
                "description": item.get("reasoning", "Discovered via post-hoc analysis"),
                "source": "guard_analyst",
                "discovered": datetime.now(UTC).strftime("%Y-%m-%d"),
            }
        )
        existing_regexes.add(suggested)  # deduplicate within batch

    return new_patterns


def append_patterns_to_file(
    new_patterns: list[dict[str, Any]],
    patterns_path: Path | None = None,
) -> int:
    """Append new patterns to the JSON patterns file.

    Returns the number of patterns added.
    """
    from app.core.llm_guard import _DEFAULT_PATTERNS_PATH

    path = patterns_path or _DEFAULT_PATTERNS_PATH
    data = json.loads(path.read_text(encoding="utf-8"))

    added = 0
    for p in new_patterns:
        category = p.get("category", "")
        if category == "prompt_extraction":
            data.setdefault("leakage_patterns", []).append(p)
        else:
            data.setdefault("injection_patterns", []).append(p)
        added += 1

    if added:
        data["updated"] = datetime.now(UTC).strftime("%Y-%m-%d")
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _logger.info("LLM Guard: %d nieuwe patronen toegevoegd aan %s", added, path)

    return added


# ── CLI ──────────────────────────────────────────────────────────────────


def _cli_summary(args: list[str]) -> None:
    """CLI: summarize blocked attempts from audit log."""
    if not args:
        print("Gebruik: python -m app.core.guard_analyst summary <logbestand>")
        sys.exit(1)

    log_path = Path(args[0])
    if not log_path.exists():
        print(f"Bestand niet gevonden: {log_path}")
        sys.exit(1)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = parse_audit_logs(lines)
    summary = summarize_blocked(entries)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def _cli_prompt(args: list[str]) -> None:
    """CLI: generate an analysis prompt from audit logs."""
    if not args:
        print("Gebruik: python -m app.core.guard_analyst prompt <logbestand>")
        sys.exit(1)

    log_path = Path(args[0])
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = parse_audit_logs(lines)
    prompt = build_analysis_prompt(entries)

    if not prompt:
        print("Geen geblokkeerde invoer gevonden in de logs.")
        sys.exit(0)

    print(prompt)


def _cli_apply(args: list[str]) -> None:
    """CLI: apply LLM analysis response to the patterns file."""
    if not args:
        print("Gebruik: python -m app.core.guard_analyst apply <analyse-response.json>")
        sys.exit(1)

    response_path = Path(args[0])
    response_text = response_path.read_text(encoding="utf-8")
    analysis = parse_analysis_response(response_text)

    if not analysis:
        print("Geen analyse-items gevonden.")
        sys.exit(0)

    new_patterns = extract_new_patterns(analysis)
    if not new_patterns:
        print("Geen nieuwe patronen gevonden (alle waren al bekend of false positives).")
        sys.exit(0)

    print(f"\n{len(new_patterns)} nieuwe patronen gevonden:")
    for p in new_patterns:
        print(f"  [{p['severity']}] {p['pattern']}")
        print(f"         {p['description']}")

    answer = input("\nToevoegen aan patronenlijst? [j/N] ").strip().lower()
    if answer in ("j", "ja", "y", "yes"):
        added = append_patterns_to_file(new_patterns)
        print(f"{added} patronen toegevoegd. Herstart de app om ze te activeren.")
    else:
        print("Geen patronen toegevoegd.")


def main() -> None:
    """CLI entrypoint."""
    args = sys.argv[1:]
    if not args:
        print("LLM Guard Analyst — post-hoc analyse van geblokkeerde queries")
        print()
        print("Commando's:")
        print("  summary <logbestand>              Samenvatting van geblokkeerde pogingen")
        print("  prompt  <logbestand>              Genereer LLM-analyse prompt")
        print("  apply   <analyse-response.json>   Pas LLM-suggesties toe op patronenlijst")
        print()
        print("Workflow:")
        print("  1. python -m app.core.guard_analyst summary audit.log")
        print("  2. python -m app.core.guard_analyst prompt audit.log > analyse-prompt.txt")
        print("  3. Voer de prompt uit in een LLM en sla de response op als analyse.json")
        print("  4. python -m app.core.guard_analyst apply analyse.json")
        sys.exit(0)

    command = args[0]
    rest = args[1:]

    commands = {
        "summary": _cli_summary,
        "prompt": _cli_prompt,
        "apply": _cli_apply,
    }

    if command not in commands:
        print(f"Onbekend commando: {command}")
        print(f"Beschikbaar: {', '.join(commands)}")
        sys.exit(1)

    commands[command](rest)


if __name__ == "__main__":
    main()
