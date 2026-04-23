"""Validatie van story-status en acceptatiecriteria voor Graaf Zeppelin.

Afgeleid van `scripts/check_story_status.py` uit Codebase-Olympus en
aangepast aan de Zeppelin-conventies:

* Storybestanden starten met ``# S##-##: Titel`` (geen "Story"-prefix).
* EPICS.md-rijen hebben de vorm
  ``| [S##-##](pad/naar/bestand.md) | status-badge | priority | beschrijving |``
  met emoji-badges (``✅ Done`` / ``🔲 Backlog`` / ``🚧 Doing``).
* Done-stories gebruiken vaak een ``## Resultaat``-sectie in plaats van
  afgevinkte acceptatiecriteria; beide vormen worden geaccepteerd.

Modi:

* ``--mode=staged`` — alleen gestageerde wijzigingen (pre-commit). Soft.
* ``--mode=full`` — hele ``stories/``-map + cross-check met ``EPICS.md``. Strict.

Returncodes: 0 (ok), 1 (soft warnings in staged-mode), 2 (harde fouten).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "stories"
EPICS_PATH = STORIES_DIR / "EPICS.md"

VALID_STATUSES = {"backlog", "doing", "done"}

# Story-ID: letters + cijfers + dash + cijfers + optionele sub-letter.
#   S14-01, S14-06a, S11-03
_ID_PATTERN = r"[A-Z]+\d*-\d{1,3}[a-z]?"

# Titel-regel van een story. Twee varianten in de repo:
#   `# S14-01: Title (context)`    (nieuwer)
#   `# S11-01 — Title`             (ouder; em-dash)
TITLE_RE = re.compile(rf"^#\s+(?P<id>{_ID_PATTERN})\s*(?::|—|–|-)\s*(?P<title>.+?)\s*$")

# Sectie-headers die we herkennen.
DOEL_RE = re.compile(r"^##\s+Doel\b", re.IGNORECASE)
RESULTAAT_RE = re.compile(r"^##\s+Resultaat\b", re.IGNORECASE)
AC_RE = re.compile(r"^##\s+Acceptatiecriteria\b", re.IGNORECASE)

# Checkbox-regel binnen een AC-sectie.
CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+")

# Status-badge in EPICS.md (zowel met als zonder emoji).
_STATUS_BADGE_RE = re.compile(
    r"(?:🔲\s*|✅\s*|🚧\s*)?(?P<status>backlog|doing|done)",
    re.IGNORECASE,
)

# EPICS.md-rij: ``| [S14-01](done/...md) | ✅ Done | HOOG | ... |`` of zonder link.
# We zoeken eerst het ID in de eerste kolom en daarna de eerste status-badge
# in de rest van de regel.
EPICS_ROW_RE = re.compile(
    rf"^\|\s*(?:\[(?P<link_id>{_ID_PATTERN})\][^|]*|(?P<bare_id>{_ID_PATTERN}))\s*\|"
    r"(?P<rest>.*)$"
)


@dataclass
class Story:
    """Een storybestand op disk."""

    id: str
    title: str
    path: Path
    status_from_location: str  # backlog/doing/done
    has_doel_or_resultaat: bool
    ac_total: int
    ac_checked: int

    @property
    def ac_open(self) -> int:
        return self.ac_total - self.ac_checked


@dataclass
class EpicEntry:
    """Een story-rij in EPICS.md."""

    story_id: str
    status: str  # backlog/doing/done
    line_number: int


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# --- Parsers ---


def parse_story(path: Path) -> Story | None:
    if not path.is_file() or path.suffix != ".md":
        return None
    status_from_location = path.parent.name
    if status_from_location not in VALID_STATUSES:
        return None

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title_match = TITLE_RE.match(lines[0]) if lines else None
    if title_match is None:
        story_id = path.stem
        title = ""
    else:
        story_id = title_match.group("id")
        title = title_match.group("title")

    has_doel_or_resultaat = False
    in_ac_section = False
    ac_total = 0
    ac_checked = 0

    for line in lines:
        if DOEL_RE.match(line) or RESULTAAT_RE.match(line):
            has_doel_or_resultaat = True
            in_ac_section = False
            continue
        if AC_RE.match(line):
            in_ac_section = True
            continue
        if in_ac_section and line.startswith("## "):
            in_ac_section = False
            continue
        if in_ac_section:
            cb = CHECKBOX_RE.match(line)
            if cb:
                ac_total += 1
                if cb.group(1).lower() == "x":
                    ac_checked += 1

    return Story(
        id=story_id,
        title=title,
        path=path,
        status_from_location=status_from_location,
        has_doel_or_resultaat=has_doel_or_resultaat,
        ac_total=ac_total,
        ac_checked=ac_checked,
    )


def parse_epics(path: Path) -> dict[str, EpicEntry]:
    entries: dict[str, EpicEntry] = {}
    if not path.is_file():
        return entries

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = EPICS_ROW_RE.match(line)
        if not match:
            continue
        story_id = (match.group("link_id") or match.group("bare_id") or "").upper()
        if not story_id:
            continue
        rest = match.group("rest") or ""
        status_match = _STATUS_BADGE_RE.search(rest)
        if not status_match:
            continue
        status = status_match.group("status").lower()
        entries[story_id] = EpicEntry(
            story_id=story_id,
            status=status,
            line_number=line_no,
        )
    return entries


def discover_stories(root: Path) -> list[Story]:
    found: list[Story] = []
    for status in VALID_STATUSES:
        folder = root / status
        if not folder.is_dir():
            continue
        for md_path in sorted(folder.glob("*.md")):
            story = parse_story(md_path)
            if story is not None:
                found.append(story)
    return found


def staged_story_paths() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    paths: list[Path] = []
    for raw in result.stdout.splitlines():
        path = REPO_ROOT / raw
        try:
            path.relative_to(STORIES_DIR)
        except ValueError:
            continue
        if path.suffix == ".md" and path.name != "EPICS.md":
            paths.append(path)
    return paths


# --- Checks ---


def check_structure(story: Story) -> CheckResult:
    """Titel, Doel-of-Resultaat, en óf AC-sectie óf Resultaat-only (voor done)."""
    result = CheckResult()
    rel = _display_path(story.path)

    if not story.title:
        result.errors.append(f"{rel}: titel-regel ontbreekt of matcht niet '# <ID>: <titel>'")

    if story.title:
        # Bestandsnamen zijn als "S14-01-cycle-check-per-edge-type.md"; we
        # vergelijken de titel-ID met de eerste twee segmenten van de stem.
        stem_parts = story.path.stem.split("-", 2)
        file_prefix = "-".join(stem_parts[:2]) if len(stem_parts) >= 2 else story.path.stem
        if story.id.upper() != file_prefix.upper():
            result.errors.append(
                f"{rel}: titel-ID '{story.id}' matcht niet bestandsnaam-prefix '{file_prefix}'"
            )

    if not story.has_doel_or_resultaat:
        # Waarschuwing (geen error): veel legacy done-stories gebruiken een
        # vrijere opbouw zonder expliciete '## Doel' of '## Resultaat'.
        # Voor nieuwe stories is dit wel de conventie.
        result.warnings.append(f"{rel}: '## Doel' of '## Resultaat'-sectie ontbreekt")

    # Acceptatiecriteria zijn verplicht voor backlog/doing (je moet weten
    # waaraan je werkt). Voor done is het een warning indien er wél AC's
    # staan maar niet alle afgevinkt.
    if story.status_from_location in {"backlog", "doing"} and story.ac_total == 0:
        # Warning (niet error): sommige legacy backlog-stories verwijzen
        # door naar een doc-bestand voor hun AC's. Voor nieuwe stories is
        # het de conventie om ze inline te hebben.
        result.warnings.append(
            f"{rel}: '## Acceptatiecriteria'-sectie ontbreekt of bevat geen checkboxes"
        )

    return result


def check_done_ac(story: Story) -> CheckResult:
    """Een story in done/ met niet-afgevinkte AC's is verdacht (warning)."""
    result = CheckResult()
    if story.status_from_location != "done":
        return result
    if story.ac_total > 0 and story.ac_open > 0:
        rel = _display_path(story.path)
        result.warnings.append(
            f"{rel}: staat in done/ maar heeft {story.ac_open} openstaand(e) "
            f"acceptatiecriterium/criteria (van {story.ac_total} totaal)"
        )
    return result


def check_status_location(story: Story, epics: dict[str, EpicEntry]) -> CheckResult:
    result = CheckResult()
    rel = _display_path(story.path)
    epic_entry = epics.get(story.id.upper())
    if epic_entry is None:
        return result
    if epic_entry.status != story.status_from_location:
        result.errors.append(
            f"{rel}: locatie zegt '{story.status_from_location}', "
            f"EPICS.md regel {epic_entry.line_number} zegt '{epic_entry.status}'"
        )
    return result


def check_orphan(story: Story, epics: dict[str, EpicEntry]) -> CheckResult:
    result = CheckResult()
    if story.id.upper() not in epics:
        rel = _display_path(story.path)
        result.warnings.append(f"{rel}: story-ID '{story.id}' niet gevonden in EPICS.md (orphan)")
    return result


def check_dead_refs(epics: dict[str, EpicEntry], story_ids: set[str]) -> CheckResult:
    result = CheckResult()
    for entry in epics.values():
        if entry.story_id.upper() not in story_ids:
            result.warnings.append(
                f"EPICS.md regel {entry.line_number}: story '{entry.story_id}' "
                f"heeft geen bestand in stories/{{backlog,doing,done}}/"
            )
    return result


# --- Mode dispatchers ---


def run_full(root: Path) -> CheckResult:
    combined = CheckResult()
    epics = parse_epics(EPICS_PATH)
    stories = discover_stories(root)
    story_ids = {s.id.upper() for s in stories}

    for story in stories:
        for check in (check_structure, check_done_ac):
            r = check(story)
            combined.errors.extend(r.errors)
            combined.warnings.extend(r.warnings)
        for cross in (check_status_location, check_orphan):
            r = cross(story, epics)
            combined.errors.extend(r.errors)
            combined.warnings.extend(r.warnings)

    dead = check_dead_refs(epics, story_ids)
    combined.errors.extend(dead.errors)
    combined.warnings.extend(dead.warnings)
    return combined


def run_staged() -> CheckResult:
    combined = CheckResult()
    epics = parse_epics(EPICS_PATH)
    paths = staged_story_paths()
    if not paths:
        return combined

    for path in paths:
        story = parse_story(path)
        if story is None:
            continue
        for check in (check_structure, check_done_ac):
            r = check(story)
            combined.errors.extend(r.errors)
            combined.warnings.extend(r.warnings)
        cross = check_status_location(story, epics)
        combined.errors.extend(cross.errors)
        combined.warnings.extend(cross.warnings)

    return combined


# --- CLI ---


def _print_report(result: CheckResult, label: str) -> None:
    if not result.errors and not result.warnings:
        print(f"✓ {label}: geen problemen.")
        return
    if result.errors:
        print(f"✗ {label}: {len(result.errors)} fout(en):")
        for err in result.errors:
            print(f"  - {err}")
    if result.warnings:
        print(f"! {label}: {len(result.warnings)} waarschuwing(en):")
        for warn in result.warnings:
            print(f"  - {warn}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("staged", "full"),
        default="full",
        help="staged: alleen gestageerde wijzigingen (pre-commit). full: hele stories/-map (CI).",
    )
    args = parser.parse_args()

    if args.mode == "staged":
        result = run_staged()
        _print_report(result, "stories (staged)")
        if result.errors:
            return 1
        return 0

    result = run_full(STORIES_DIR)
    _print_report(result, "stories (full)")
    if result.errors:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
