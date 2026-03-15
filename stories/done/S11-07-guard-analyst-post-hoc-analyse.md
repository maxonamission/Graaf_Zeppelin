# S11-07 — Guard Analyst: post-hoc analyse van geblokkeerde queries

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: M
**Status:** ✅ Afgerond

## Doel

Een workflow en tooling voor periodieke analyse van geblokkeerde LLM Guard-queries,
zodat nieuwe injectiepatronen worden ontdekt en de patronenlijst groeit zonder
real-time LLM-overhead.

## Aanleiding

De regex-gebaseerde LLM Guard vangt bekende patronen, maar creatieve varianten
kunnen er doorheen glippen. Een real-time LLM-classifier is disproportioneel
(verdubbelt latentie en kosten), maar periodieke batch-analyse van audit logs
biedt de beste ROI: lage kosten, geen latentie-impact, en het levert concrete
nieuwe patronen op.

### Afweging: real-time vs. post-hoc

| Maatregel | Latentie | Kosten | Effectiviteit | Aanbeveling |
|-----------|----------|--------|---------------|-------------|
| Real-time LLM classifier | +1-3s per request | 2x LLM-kosten | Hoog | **Niet nu** — pas bij open API of LLM met tools |
| Post-hoc batch-analyse | 0 (async) | Minimaal | Gemiddeld-Hoog | **Ja** — periodiek, beste ROI |

## Acceptatiecriteria

- [x] `guard_analyst.py` module met functies voor log-parsing, samenvatting en LLM-analyse
- [x] CLI interface: `python -m app.core.guard_analyst <command>`
- [x] Commando `summary`: samenvatting van geblokkeerde pogingen per patroon/gebruiker
- [x] Commando `prompt`: genereert een LLM-prompt voor analyse van geblokkeerde invoer
- [x] Commando `apply`: past LLM-suggesties toe op de patronenlijst (met bevestiging)
- [x] Dedupliceert geblokkeerde invoer voordat het naar de LLM gaat
- [x] Valideert voorgestelde regex-patronen vóór toevoeging
- [x] Voorkomt duplicaten met bestaande patronen
- [x] Tests voor alle kernfuncties

## Workflow

```
1. Verzamel audit logs
   ↓
2. python -m app.core.guard_analyst summary audit.log
   → Overzicht: hoeveel blokkades, welke patronen, welke gebruikers
   ↓
3. python -m app.core.guard_analyst prompt audit.log > analyse-prompt.txt
   → Genereer een LLM-prompt met geblokkeerde invoer
   ↓
4. Voer de prompt uit in een LLM (handmatig of via API)
   → Sla de response op als analyse.json
   ↓
5. python -m app.core.guard_analyst apply analyse.json
   → Toont voorgestelde patronen, vraagt bevestiging
   → Voegt toe aan data/llm_guard_patterns.json
   ↓
6. Herstart de app om nieuwe patronen te activeren
```

## Bestanden

| Bestand | Wijziging |
|---------|-----------|
| `app/core/guard_analyst.py` | **Nieuw** — analyse module + CLI |
| `tests/test_llm_guard.py` | **Uitgebreid** — 8 nieuwe tests voor guard analyst |

## Testdekking

| Testklasse | Tests | Beschrijving |
|------------|-------|-------------|
| `TestGuardAnalyst` | 8 | Log parsing, samenvatting, prompt generatie, response parsing, patroon-extractie, file-append |

## Relatie met andere stories

- **S11-05**: De patronen worden geladen uit het JSON-bestand dat in S11-06 is geïntroduceerd
- **S11-06**: De analyst voedt nieuwe patronen terug naar het JSON-bestand
- **S11-04**: De audit logs die worden geanalyseerd zijn aangemaakt door de audit logger
