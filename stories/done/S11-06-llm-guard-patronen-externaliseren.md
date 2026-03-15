# S11-06 — LLM Guard patronen externaliseren naar JSON

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** ✅ Afgerond

## Doel

De hardcoded regex-patronen in `llm_guard.py` externaliseren naar een configureerbaar
JSON-bestand, zodat nieuwe patronen kunnen worden toegevoegd zonder code-deploy.

## Aanleiding

De initiële LLM Guard (S11-05) bevat hardcoded regex-patronen voor prompt injection
en system prompt leakage detectie. Dit werkt, maar heeft twee nadelen:
1. Nieuwe patronen toevoegen vereist een code-deploy
2. De patronen zijn niet inzichtelijk voor niet-technische stakeholders

## Acceptatiecriteria

- [x] Patronen staan in `data/llm_guard_patterns.json` met metadata per patroon
      (category, lang, severity, description)
- [x] `llm_guard.py` laadt patronen uit JSON bij module-import
- [x] Fallback naar ingebouwde patronen als het JSON-bestand ontbreekt of onleesbaar is
- [x] `reload_patterns()` functie om patronen te herladen zonder app-herstart
- [x] `get_patterns_info()` functie voor metadata over geladen patronen
- [x] Ongeldige regex-patronen worden overgeslagen met warning (geen crash)
- [x] Alle bestaande tests blijven slagen
- [x] Nieuwe tests voor JSON-loading, fallback, custom patronen, ongeldige regex

## Patroon-schema

```json
{
  "version": "1.0.0",
  "updated": "2026-03-15",
  "injection_patterns": [
    {
      "pattern": "ignore\\s+previous\\s+instructions",
      "category": "instruction_override",
      "lang": "en",
      "severity": "high",
      "description": "Attempts to override system instructions"
    }
  ],
  "leakage_patterns": [...]
}
```

## Bestanden

| Bestand | Wijziging |
|---------|-----------|
| `data/llm_guard_patterns.json` | **Nieuw** — 18 injection + 7 leakage patronen met metadata |
| `app/core/llm_guard.py` | **Gewijzigd** — JSON-loading, fallback, reload, info functies |
| `tests/test_llm_guard.py` | **Uitgebreid** — 6 nieuwe tests voor pattern loading |

## Testdekking

| Testklasse | Tests | Beschrijving |
|------------|-------|-------------|
| `TestPatternLoading` | 6 | JSON laden, fallback, custom patronen, ongeldige regex |
