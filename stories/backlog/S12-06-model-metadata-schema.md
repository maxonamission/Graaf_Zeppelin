# S12-06 — Model-metadata schema uitbreiden

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: HOOG
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

Het huidige model-JSON bevat metadata die specifiek is voor KNSB (project, versie, bronnen).
Voor multi-domein gebruik moet het schema worden uitgebreid met velden die de app nodig heeft
om zich automatisch aan te passen aan een nieuw domein.

## Huidig schema (`metadata`)

```json
{
  "metadata": {
    "project": "Sportdeelnamemodel KNSB",
    "version": "2.3.0",
    "date": "2026-02-20",
    "sources": { ... },
    "summary": { "total_nodes": 69, "domains": { ... }, ... },
    "graph_metrics": { ... }
  }
}
```

## Gewenst schema (uitbreiding)

```json
{
  "metadata": {
    "project": "Sportdeelnamemodel KNSB",
    "version": "2.3.0",
    "date": "2026-02-20",
    "domain_name": "Sportdeelname",
    "domain_slug": "sportdeelname",
    "language": "nl",
    "persona": "Je bent een beleidsadviseur gespecialiseerd in sportdeelname",
    "target_audience": "Beleidsmedewerkers bij sportbonden",
    "description_short": "Causaal model voor sportdeelname bij de KNSB",
    "example_questions": {
      "reasoning": [
        "Wat gebeurt er als we investeren in betere coaching?",
        "Welke factoren hebben de meeste invloed op sportdeelname?"
      ],
      "wizard": [
        "Hoe kunnen we de sportdeelname onder jongeren verhogen?"
      ]
    },
    "sources": { ... },
    "summary": { ... },
    "graph_metrics": { ... }
  }
}
```

## Acceptatiecriteria

- [ ] Schema-documentatie beschrijft alle metadata-velden met type en default
- [ ] `CausalDAG` parseert de nieuwe velden en maakt ze beschikbaar als properties
- [ ] Nieuwe velden zijn optioneel — bestaande modellen laden zonder fout
- [ ] Property `dag.domain_name` geeft `metadata.domain_name` of fallback `metadata.project`
- [ ] Property `dag.example_questions` geeft dict met reasoning/wizard arrays (of lege arrays)
- [ ] Property `dag.persona` geeft persona-string of generieke fallback
- [ ] Property `dag.language` geeft taalcode (default "nl")
- [ ] Bestaand sportdeelnamemodel wordt bijgewerkt met de nieuwe velden
- [ ] Bestaande tests slagen

## Technische aanpak

1. Voeg properties toe aan `CausalDAG` die uit `self.metadata` lezen met fallbacks
2. Werk het sportdeelname JSON-model bij met de extra metadata-velden
3. Documenteer het schema in een commentaarblok of apart bestand

## Afhankelijkheden

- Geen (fundament voor S12-02, S12-03 en S12-04)
- Aanbevolen volgorde: S12-06 → S12-01 → S12-05 → S12-02 → S12-03 → S12-04
