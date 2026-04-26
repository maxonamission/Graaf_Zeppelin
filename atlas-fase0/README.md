# Fase 0 deliverables — promote_reference.py + paths.yml

Tool voor promotie van literatuur-referenties van project-eigen registers
naar het gedeelde register `A_/literatuur/gedeeld_register.json`.

## Plaatsing in atlas-repo

```
codebase_atlas/
├── _scripts/
│   ├── promote_reference.py        ← uit dit pakket
│   └── paths.yml                   ← uit dit pakket
└── A_Modulaire Modelarchitectuur/literatuur/
    └── gedeeld_register.json       ← uit atlas-fase0-gedeeld-register.json
```

`paths.yml` mag ook ergens anders staan; geef dan `--config <pad>` mee.

## Dependency

```bash
pip install pyyaml
```

Geen verdere dependencies. Werkt op Python 3.10+.

## Gebruik

**Promotie van een bron die in twee modellen voorkomt:**

```bash
python _scripts/promote_reference.py REF_Edmondson_1999 --from L2 D1
```

**Met optionele concept-tags:**

```bash
python _scripts/promote_reference.py REF_Edmondson_1999 \
    --from L2 D1 \
    --concepts psychological-safety team-learning
```

**Dry-run om te checken zonder te schrijven:**

```bash
python _scripts/promote_reference.py REF_Edmondson_1999 \
    --from L2 D1 --dry-run
```

**Vanuit een andere werkdirectory:**

```bash
python /pad/naar/promote_reference.py REF_Edmondson_1999 \
    --from L2 D1 \
    --repo-root /pad/naar/codebase_atlas \
    --config /pad/naar/codebase_atlas/_scripts/paths.yml
```

## Wat het doet

1. Valideert ref_id-formaat (`REF_<Author>_<Year>`, optioneel disambig-suffix
   als in `REF_Edmondson_1999a`).
2. Controleert dat de bron nog niet in het gedeelde register staat.
3. Zoekt entry in opgegeven model-registers; verzamelt waarschuwingen voor
   modellen waarvan het register nog niet bestaat (L1/C1 in huidige toestand).
4. Strip model-specifieke velden zoals `avv_usage`, `sdm_usage`,
   `thema_codes`, `shared` (configureerbaar in `paths.yml`).
5. Voegt `used_by[]` toe met de modellen waarin de bron daadwerkelijk
   gevonden is (niet noodzakelijk alle opgegeven modellen).
6. Voegt `concepts[]` toe als opgegeven.
7. Schrijft naar het gedeelde register; werkt `total_references`, `date`
   en `change_log` bij.
8. Markeert lokale registers met `shared: true` voor de gepromoveerde entry.

## Wat het niet doet (bewust)

- **Geen overlap-detectie tussen modellen.** Dat is Fase 1 (aparte
  diff-tool).
- **Geen fuzzy matching** op (auteur, jaar, titel) — alleen exacte ref_id.
  Voor L3 (T-codes) eerst Fase 2 (schema-uitbreiding) doorlopen, anders
  zal het script niets vinden in L3.
- **Geen demotion.** Verwijdering uit gedeeld register doe je handmatig
  + zet `deprecated: true` (per governance in
  `A_/literatuur/README.md`).
- **Geen hercheck van bestaande entries.** Als je metadata wijzigt in
  een lokaal register na promotie, propageert dat niet automatisch.

## Validaties en waarschuwingen

| Situatie | Gedrag |
|---|---|
| Ongeldig ref_id-formaat | ERROR + exit 1 |
| Ref_id al in gedeeld register | ERROR + exit 1 |
| Onbekend model in `--from` | WARNING (skip) |
| Lokaal register-pad bestaat niet | WARNING (skip) |
| Ref_id in <2 modellen gevonden | WARNING (toch promoten als gebruiker dat wil) |
| `--from A_` opgegeven | Geen 2-modellen-warning (architecturele kandidaten) |

De 2-modellen-regel is een *waarschuwing*, geen blokkade — voor
architecturele kandidaten (`--from A_`) is één model voldoende.

## Pad-aanpassing na harmonisatie

Als de folder-structuur-harmonisatie (zie
`A_/docs/dwarsdoorsnede_modellenstructuur.md`) wordt doorgevoerd, pas
alleen `paths.yml` aan. Het script zelf hoeft niet te wijzigen.

Als L1 of C1 een gestructureerd register krijgen (Fase 3), voeg dan de
juiste paden toe aan `paths.yml` of bevestig dat de huidige paden
(`L1_referenties.json`, `C1_referenties.json`) passen.

## Snel testen na plaatsing

```bash
# 1. Dry-run met een entry uit Fase 0 (architecturele kandidaat)
python _scripts/promote_reference.py REF_Edmondson_1999 --from A_ --dry-run
# verwacht: ERROR omdat REF_Edmondson_1999 al in gedeeld register staat

# 2. Dry-run met een fictief ref_id om validatie te zien
python _scripts/promote_reference.py REF_Test_2024 --from L2 D1 --dry-run
# verwacht: ERROR omdat ref_id niet in genoemde registers staat
```

## Volgende stap

Fase 1: cross-model overlap-detectie L2 ∩ D1. Aparte tool:
`_scripts/find_shared_refs.py` (nog te bouwen). Dat tool produceert een
lijst van kandidaat-`ref_id`s die je dan via dit script kunt promoveren.
