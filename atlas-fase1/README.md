# Fase 1 — meting: gedeelde literatuur-referenties

Hybride benadering om de keuze tussen handmatige en fuzzy match in
Fase 1 te informeren. Dit pakket bevat één tool die tellingen + een
leesbaar mismatch-rapport produceert; de mens beoordeelt vervolgens de
mismatch-lijst en de uniek-per-model steekproef.

## Plaatsing in atlas-repo

```
codebase_atlas/
└── _scripts/
    ├── find_shared_refs.py        ← uit dit pakket
    ├── promote_reference.py        ← uit atlas-fase0/
    └── paths.yml                   ← uit atlas-fase0/
```

`find_shared_refs.py` hergebruikt dezelfde `paths.yml` als `promote_reference.py`.

## Dependency

```bash
pip install pyyaml
```

Werkt op Python 3.10+.

## Gebruik

**Default — vergelijk L2 ↔ D1, alleen tellingen naar stdout:**

```bash
python _scripts/find_shared_refs.py --from L2 D1
```

Voorbeeld output:

```
=== L2 ↔ D1 ===
  L2: 234 entries
  D1: 187 entries
  exacte ref_id-matches: 23
  fuzzy kandidaten (auteur+jaar, andere ref_id): 11
  uniek in L2: 200
  uniek in D1: 153
```

**Met markdown-rapport voor handmatige review:**

```bash
python _scripts/find_shared_refs.py --from L2 D1 --out fase1-meting.md
```

Het rapport bevat:
- Tellingen.
- Tabel met **exacte matches** (directe promotie-kandidaten).
- Tabel met **fuzzy kandidaten** (zelfde auteur+jaar, andere `ref_id` —
  zij-aan-zij vergelijking).
- **Steekproef van 10 uniek-per-model entries** (eerste 10 alfabetisch
  op `ref_id`).

**Andere modelparen:**

```bash
python _scripts/find_shared_refs.py --from L2 L3 --out l2-l3-meting.md
```

NB: L3 gebruikt T-codes naast `ref_id`, dus exacte ref_id-matching
levert weinig op tot Fase 2 (schema-uitbreiding) is uitgevoerd. Fuzzy
op (auteur, jaar) werkt wel.

## Wat het meet

| Categorie | Definitie |
|---|---|
| **Exacte match** | Identieke `ref_id` in beide registers |
| **Fuzzy kandidaat** | Genormaliseerde eerste-auteur-familienaam (lower + diacritics-strip) + zelfde jaar, maar verschillende `ref_id` |
| **Uniek** | Wel in dit register, niet in het andere |

Fuzzy is een **kandidaat-signaal**, geen automatische match. Twee
verschillende werken van Edmondson 1999 zouden bv. dezelfde fuzzy-key
hebben. Daarom: handmatige beoordeling van het rapport.

## Hoe te lezen

1. **Cijfers eerst**: kleine fuzzy-set (<10) → conventies zijn
   grotendeels consistent, fuzzy-matching nodig voor randgevallen.
   Grote fuzzy-set (>30) → verschillende ref_id-conventies tussen
   modellen, harmonisatie binnen modellen aangewezen vóór bulk-promotie.
2. **Fuzzy-tabel**: kijk naar de titels naast elkaar. Identiek of
   bijna-identiek → harmonisatie van `ref_id` (één van beide aanpassen).
   Verschillend → toevallige auteur+jaar-overlap, geen match.
3. **Uniek-steekproef**: zie je bekende klassiekers in de uniek-lijst van
   één model? Dan is de andere die mist en ligt promotie voor de hand
   zodra dat tweede model die bron toevoegt.

## Wat het niet doet (bewust)

- **Geen automatische promotie** — dat is `promote_reference.py`.
- **Geen titel-fuzzy-match** — alleen (auteur, jaar). Titel-vergelijking
  is volume-intensief en levert veel ruis bij vertaalde of subtitel-
  variaties. Bewuste keuze om eerst minimaal te meten.
- **Geen multi-model-vergelijking** in één run — alleen paarsgewijs.
  Voor L2 ↔ L3 ↔ D1 draai je het drie keer.
- **Geen schrijven naar registers** — pure analyse, alleen rapport-output.

## Volgende stap

Op basis van het rapport beslis je:

- **Veel exacte matches, weinig fuzzy** → directe batch-promotie via
  `promote_reference.py` voor de exacte matches; korte handmatige
  ronde voor fuzzy.
- **Weinig exacte, veel fuzzy** → eerst lokale `ref_id`-harmonisatie
  in één van beide modellen voordat je promoveert.
- **Beide laag** → registers raken weinig dezelfde bronnen; rust hier
  niet langer op dan nodig en ga door naar L3/L1/C1.
