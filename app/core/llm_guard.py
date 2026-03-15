"""LLM Guard — Mitigations for OWASP Top 10 for LLM Applications.

Covers:
- LLM01: Prompt Injection detection
- LLM05: Output sanitization (strip HTML/scripts)
- LLM07: System prompt leakage detection

Patterns are loaded from ``data/llm_guard_patterns.json`` at module import.
Add new patterns to that file without a code deploy — restart the app to pick
them up.  If the file is missing or unreadable the guard falls back to a
built-in baseline so protection is never absent.
"""

from __future__ import annotations

import html
import json
import logging
import re
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

# ── Pattern loading ──────────────────────────────────────────────────────

_DEFAULT_PATTERNS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "llm_guard_patterns.json"

# Built-in fallback — used only when the JSON file cannot be loaded.
_FALLBACK_INJECTION = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"negeer\s+(alle\s+)?vorige\s+instructies",
    r"vergeet\s+(alle\s+)?eerdere\s+instructies",
    r"disregard\s+(all\s+)?(above|prior|previous)",
    r"you\s+are\s+now\s+(a|an)\b",
    r"je\s+bent\s+nu\s+(een|het)\b",
    r"new\s+instructions?\s*:",
    r"nieuwe\s+instructies?\s*:",
    r"system\s*prompt\s*:",
    r"<\s*/?\s*system\s*>",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<\s*SYS\s*>>",
    r"```\s*system",
    r"ADMIN\s*MODE",
    r"DAN\s*MODE",
    r"jailbreak",
    r"do\s+anything\s+now",
]

_FALLBACK_LEAKAGE = [
    r"(what|show|reveal|repeat|print).{0,30}system\s*prompt",
    r"(wat|toon|laat).{0,30}systeem\s*prompt",
    r"(what|show|reveal).{0,30}(your|initial)\s*instructions",
    r"(wat|toon).{0,30}(je|jouw)\s*instructies",
    r"herhaal\s+(je|jouw|de)\s+(instructies|prompt)",
    r"repeat\s+(your|the)\s+(instructions|prompt)",
    r"(what|how)\s+were\s+you\s+(instructed|prompted|configured)",
]


def _compile_patterns(raw: list[str]) -> list[re.Pattern[str]]:
    compiled = []
    for p in raw:
        try:
            compiled.append(re.compile(p, re.IGNORECASE))
        except re.error as exc:
            _logger.warning("Ongeldige regex in LLM Guard patronen, overgeslagen: %r (%s)", p, exc)
    return compiled


def _load_patterns(path: Path | None = None) -> tuple[list[re.Pattern[str]], list[re.Pattern[str]], dict[str, Any]]:
    """Load patterns from JSON, returning (injection, leakage, raw_data).

    Falls back to built-in patterns on any error.
    """
    path = path or _DEFAULT_PATTERNS_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        injection_raw = [p["pattern"] for p in data.get("injection_patterns", [])]
        leakage_raw = [p["pattern"] for p in data.get("leakage_patterns", [])]
        _logger.info(
            "LLM Guard: %d injection + %d leakage patronen geladen uit %s",
            len(injection_raw), len(leakage_raw), path,
        )
        return _compile_patterns(injection_raw), _compile_patterns(leakage_raw), data
    except Exception as exc:
        _logger.warning(
            "LLM Guard: kan %s niet laden (%s), fallback naar ingebouwde patronen",
            path, exc,
        )
        return (
            _compile_patterns(_FALLBACK_INJECTION),
            _compile_patterns(_FALLBACK_LEAKAGE),
            {},
        )


# Module-level state — loaded once at import, reloadable via reload_patterns().
_INJECTION_PATTERNS: list[re.Pattern[str]]
_LEAKAGE_PATTERNS: list[re.Pattern[str]]
_PATTERNS_DATA: dict[str, Any]
_INJECTION_PATTERNS, _LEAKAGE_PATTERNS, _PATTERNS_DATA = _load_patterns()


def reload_patterns(path: Path | None = None) -> dict[str, int]:
    """Reload patterns from disk.  Returns counts for confirmation."""
    global _INJECTION_PATTERNS, _LEAKAGE_PATTERNS, _PATTERNS_DATA  # noqa: PLW0603
    _INJECTION_PATTERNS, _LEAKAGE_PATTERNS, _PATTERNS_DATA = _load_patterns(path)
    return {
        "injection_patterns": len(_INJECTION_PATTERNS),
        "leakage_patterns": len(_LEAKAGE_PATTERNS),
        "version": _PATTERNS_DATA.get("version", "fallback"),
    }


def get_patterns_info() -> dict[str, Any]:
    """Return metadata about the currently loaded patterns."""
    return {
        "version": _PATTERNS_DATA.get("version", "fallback"),
        "updated": _PATTERNS_DATA.get("updated", "unknown"),
        "injection_count": len(_INJECTION_PATTERNS),
        "leakage_count": len(_LEAKAGE_PATTERNS),
        "source": str(_DEFAULT_PATTERNS_PATH) if _PATTERNS_DATA else "built-in fallback",
    }


# ── LLM01: Prompt Injection ─────────────────────────────────────────────


def check_prompt_injection(user_input: str) -> str | None:
    """Check user input for common prompt injection patterns.

    Returns the matched pattern description if injection is detected,
    or None if the input appears safe.
    """
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(user_input)
        if match:
            return match.group(0)
    return None


# ── LLM05: Output Sanitization ──────────────────────────────────────────

# Tags that should never appear in LLM output served to a browser.
_DANGEROUS_TAGS = re.compile(
    r"<\s*/?\s*(script|iframe|object|embed|form|input|link|meta|base|svg\s+onload)\b",
    re.IGNORECASE,
)


def sanitize_llm_output(text: str) -> str:
    """Sanitize LLM output to prevent XSS when rendered in a browser.

    - Escapes HTML entities in dangerous tag constructs
    - Preserves markdown-friendly content (bold, lists, headers)
    """
    if _DANGEROUS_TAGS.search(text):
        # Escape all HTML in the output to neutralize any injected tags.
        text = html.escape(text, quote=False)
    return text


# ── LLM07: System Prompt Leakage ────────────────────────────────────────


def check_prompt_leakage_attempt(user_input: str) -> str | None:
    """Detect if the user is trying to extract the system prompt.

    Returns the matched pattern description if detected, or None.
    """
    for pattern in _LEAKAGE_PATTERNS:
        match = pattern.search(user_input)
        if match:
            return match.group(0)
    return None
