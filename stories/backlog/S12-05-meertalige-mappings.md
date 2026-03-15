# S12-05 — Polarity/strength mappings meertalig maken

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: XS
**Status:** 🔲 Backlog

## Doel

De `_POLARITY_MAP` en `_STRENGTH_MAP` in `dag_engine.py` bevatten alleen Nederlandse
termen ("positief", "sterk", "midden"). Modellen in andere talen of met Engelse labels
moeten ook correct ingelezen worden.

## Bevindingen

| Locatie | Probleem |
|---------|----------|
| `app/core/dag_engine.py:22-28` | `_POLARITY_MAP` kent alleen NL + EN, maar mist "variable" (EN) |
| `app/core/dag_engine.py:30-35` | `_STRENGTH_MAP` kent alleen NL ("sterk"/"midden"/"zwak"), geen EN equivalenten |

## Acceptatiecriteria

- [ ] `_POLARITY_MAP` bevat NL én EN termen: positive/positief, negative/negatief, variable/variabel
- [ ] `_STRENGTH_MAP` bevat NL én EN termen: strong/sterk, medium/midden, weak/zwak
- [ ] Onbekende termen worden graceful afgehandeld (fallback naar "positive" / 0.5)
- [ ] Optioneel: model-metadata kan een custom mapping bevatten die de defaults overschrijft
- [ ] Bestaande tests slagen

## Technische aanpak

```python
_POLARITY_MAP = {
    "positief": "positive", "negatief": "negative", "variabel": "variable",
    "positive": "positive", "negative": "negative", "variable": "variable",
}

_STRENGTH_MAP = {
    "sterk": 0.8, "midden": 0.5, "zwak": 0.2,
    "strong": 0.8, "medium": 0.5, "weak": 0.2,
}
```

## Afhankelijkheden

- Geen (kan onafhankelijk worden opgepakt, kleinste story)
