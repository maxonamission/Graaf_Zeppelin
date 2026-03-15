"""LLM Guard — Mitigations for OWASP Top 10 for LLM Applications.

Covers:
- LLM01: Prompt Injection detection
- LLM05: Output sanitization (strip HTML/scripts)
- LLM07: System prompt leakage detection
"""

from __future__ import annotations

import html
import re

# ── LLM01: Prompt Injection ─────────────────────────────────────────────

# Patterns that indicate prompt injection attempts (case-insensitive).
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
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
]


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

_LEAKAGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"(what|show|reveal|repeat|print).{0,30}system\s*prompt",
        r"(wat|toon|laat).{0,30}systeem\s*prompt",
        r"(what|show|reveal).{0,30}(your|initial)\s*instructions",
        r"(wat|toon).{0,30}(je|jouw)\s*instructies",
        r"herhaal\s+(je|jouw|de)\s+(instructies|prompt)",
        r"repeat\s+(your|the)\s+(instructions|prompt)",
        r"(what|how)\s+were\s+you\s+(instructed|prompted|configured)",
    ]
]


def check_prompt_leakage_attempt(user_input: str) -> str | None:
    """Detect if the user is trying to extract the system prompt.

    Returns the matched pattern description if detected, or None.
    """
    for pattern in _LEAKAGE_PATTERNS:
        match = pattern.search(user_input)
        if match:
            return match.group(0)
    return None
