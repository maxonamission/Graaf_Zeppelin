# Instructie — Literatuurregisters & gedeeld register Modelbouw

**Repo waar dit thuishoort:** `maxonamission/codebase_atlas`
**Branch:** vermoedelijk verder op `claude/import-action-plan-OSoWH`
of een nieuwe branch
**Datum hand-off:** 2026-04-26

## Hoe deze instructie te gebruiken

Dit document is een hand-off vanuit een sessie die per ongeluk in
`graaf_zeppelin` is gevoerd. Alle deliverables zijn dáár gecommit en
moeten naar atlas worden overgeheveld. De bevindingen, beslissingen
en open vragen staan hieronder zodat een nieuwe sessie tegen de juiste
repo kan voortbouwen zonder vanaf nul te beginnen.

**Praktisch eerste werk in de nieuwe sessie:**
1. Lees deze instructie helemaal door.
2. Haal de vier deliverables uit `graaf_zeppelin` (zie sectie
   *Reeds geleverd*).
3. Plaats ze op de juiste paden in atlas (zie idem).
4. Vervolg met de stappen in *Aanbevolen vervolg*.

---

## Oorspronkelijke vraag (begin van het werk)

> *"In de architectuurfolder staat nu de map literatuur met een skeleton
> voor het gedeelde literatuur register. Presenteer me het plan om de
> literatuurvermeldingen uit de andere folders op te halen. Als je
> constateert dat het eerst nodig is om de literatuurregisters lokaal te
> harmoniseren en integreren met de modellen, laat dat uiteraard dan ook
> eerst weten."*

## Aanvullende instructie (door gebruiker in te vullen)

> *[hier zet de gebruiker de aanvullende instructie voor de nieuwe sessie]*

---

## Status in één blik (op 26 april 2026)

- **Skeleton** in `A_/literatuur/gedeeld_register.json` aangemaakt door
  de gebruiker (versie 0.1, 0 entries).
- **Acht architecturele kandidaten** uit de README §6 zijn als batch
  klaargezet (verified=false): Sterman 2000, Edmondson 1999, Schein 2010,
  Teece 2007, Deci & Ryan 2000, Bronfenbrenner 1979, Coleman 1988,
  Kozlowski & Klein 2000.
- **Promotie-tool** `promote_reference.py` + `paths.yml` gebouwd en
  syntax-getest.
- **Meet-tool** `find_shared_refs.py` gebouwd en gedraaid tegen L2 ↔ D1.
- **Belangrijke bevinding tijdens uitvoer**: de modelregisters hebben
  schema's die fundamenteel verschillen — de oorspronkelijke aanname
  "L2 + D1 zijn schema-compatibel" was onjuist. Voortzetting vraagt
  schema-harmonisatie eerst (zie sectie *Drie kritieke punten* en
  *Generiek schema voorstel*).
- **Vier modellen hebben JSON-registers** (L2, L3, D1, A_-skeleton).
  **Twee hebben markdown-only** (L1 tabel-vorm parseable; C1 narrative
  essay nauwelijks parseable). JSON-conversie van L1 + C1 staat als
  separate todo.

---

## Bevindingen per model

| Model | Format | Pad | Aantal | Identifier-conventie |
|---|---|---|---|---|
| **L1 VM** | markdown-tabel | `L1_.../literatuur/MO 0.09 Literatuuroverzicht Vermogensmodel.md` | ~204 (L001–L204) | `LNNN` in tabel-kolom "ID" |
| **L2 AVV** | JSON | `L2_.../literatuur/AVV_D1_referenties.json` | 97 | `ref_id` zoals `REF_deci_ryan_2000` (lowercase, multi-author met underscores) |
| **L3 NSkiV** | JSON | `L3_.../literatuur/register/literatuurregister_v2.json` | 900 | `lit_id` zoals `LIT_001` (sequence) |
| **D1 SDM** | JSON | `D1_.../literatuur/SDM_D1_referenties.json` | 66 | `id` zoals `L001` (sequence) |
| **C1 CMD** | markdown-narrative | `C1_.../literatuur/MDW_Lit_Data_Literacy_Organizations.md` (+ 1 ander) | onbekend; inline citations | geen identifier-systeem |
| **A_ gedeeld** | JSON (skeleton) | `A_.../literatuur/gedeeld_register.json` | 0 (8 klaargezet, niet toegepast) | `ref_id` in `REF_<Author>_<Year>` (protocol §6.2 voorbeeld) |

**Belangrijke observatie over L2's bestandsnaam**: `AVV_D1_referenties` —
de "D1" hier verwijst naar **Deliverable 1 van AVV**, NIET het D1-model
(Sportdeelnamemodel). Naamgeving is verwarrend en komt waarschijnlijk
terug in de folder-harmonisatie (zie
`A_/docs/dwarsdoorsnede_modellenstructuur.md`).

## Schema-vergelijking JSON-registers

| Generiek concept | A_ (gedeeld) | L2 (AVV_D1) | L3 (literatuurregister_v2) | D1 (SDM_D1) |
|---|---|---|---|---|
| identifier | `ref_id` (REF_…) | `ref_id` (REF_…) | `lit_id` (LIT_NNN) | `id` (LNNN) |
| short cite-key | `cite_key` | `cite_key` | — | — |
| auteurs | `authors[{family,given}]` | `authors[{family,given}]` | `auteurs` (string `"Last, F.J"`) | `authors_raw` (string, full APA-style) |
| jaar | `year` (int) | `year` (int) | `jaar` (int) | `year` (int) |
| titel | `title` | `title` | `titel` | (ingebed in `apa7`) |
| volledige citatie | gedistribueerd over velden | `source`/`volume`/`issue`/`pages`/`doi` | `apa_citation` (volledige string) | `apa7` (volledige string) |
| volume / issue / pages | ja | ja | nee (gevangen in apa) | nee (gevangen in apa) |
| doi | `doi` | `doi` | nee | nee |
| url | nee | nee | `url` | nee |
| type | `type` (enum) | `type` (enum: journal_article/book/...) | `categorie` (vrije tekst, **237 unieke waarden!**) | `type` (enum: Node/Edge/Beiden/Theoretisch) |
| evidence-niveau | `evidence_class` (recommended) | indirect via `verified` | `niveau` (A=206 / B=657 / C=37) | `status` (A=36 / B=22 / `-`=8) |
| verified-vlag | `verified` (bool) | `verified` (bool) + `verification_notes` | impliciet via niveau | `reviewed` (bool) |
| usage in model | `used_by[]` (cross-model) | `avv_usage[{file,context,element_id,usage_type}]` | `themas[int]` + `kernconcepten[str]` | `refs_nodes[]` + `refs_edges[]` + `domain` + `theme` |
| concept-tags | `concepts[]` | `tags[]` | `kernconcepten[]` | — |
| extra | `deprecated`, `verification_notes` | `abstract_summary`, `edition`, `editors`, `publisher`, `duplicate_of` | `notities` (29/900) | `_placeholder_fields` |

## Identifier-format steekproef (letterlijk)

```
L2:  REF_deci_ryan_2000, REF_schein_2010, REF_wann_2006,
     REF_edmondson_1999, REF_cuskelly_2006
L3:  LIT_001, LIT_002, LIT_003, ...
D1:  L001, L002, L003, ...
```

## Auteurs-representatie steekproef (letterlijk)

```
L2:  [{"family": "Deci", "given": "Edward L."},
      {"family": "Ryan", "given": "Richard M."}]
L3:  "Fogg, B.J"  (gewoon string, soms met trailing whitespace)
D1:  "Scheerder, J., Vandermeerschen, H., Van Tuyckom, C., …"
     (full author-list als één string)
```

## Markdown-registers (L1 + C1)

**L1 — `MO 0.09 Literatuuroverzicht Vermogensmodel.md`:**

YAML frontmatter (versie 2.2, datum 2026-02-04, status "In opbouw"),
daarna een tabel met kolommen:

| ID | Bron (APA) | Type | Referenties | Domein | Kernthema | Status | Herkomst |

204 entries (L001–L204). Type-enum: Node / Edge / Node + Edge / Slider /
Theoretisch. Status: A/B-equivalent (empirische sterkte). Referenties
verwijzen naar nodes (N1–N29). Het bestand `RAPPORT_Literatuuroverzicht_
Analyse.md` aggregeert dezelfde data per node.

**Conversie naar JSON is haalbaar**: pandas of een simpele markdown-table-
parser kan elke rij omzetten. Per rij: APA-citatie parsen voor auteurs +
jaar + titel.

**C1 — `MDW_Lit_Data_Literacy_Organizations.md`:**

Academisch literatuur-essay zonder tabelstructuur. Inline citations als
`Brynjolfsson and McElheran (2016, 2019)`, `(Ridsdale et al., 2015)`,
`(Ransbotham et al., 2015–2022)`, etc.

**Conversie naar JSON is geen automatisch werk**: vereist NLP-extractie
of handmatige verwerking. Dit moet als aparte story behandeld worden.

---

## Drie kritieke punten — neem deze mee in besluitvorming

### 1. ref_id-conventie-conflict (protocol vs L2-praktijk)

- Protocol §6.2 voorbeeld: `REF_Edmondson_1999a` (hoofdletter, single
  author).
- L2's eigen register: `REF_deci_ryan_2000`, `REF_scheerder_etal_2011`
  (lowercase, multi-author met `_`-scheiding, `etal`-suffix).
- De Fase 0 batch (zie deliverables) gebruikt momenteel hoofdletter zoals
  het protocol voorbeeld. Mijn `promote_reference.py` regex eist
  hoofdletter (`^REF_[A-Z]…`).
- **Beslissing nodig vóór andere werkzaamheden**: protocol-stijl
  hanteren of L2-praktijk hanteren. L2-praktijk is realistischer voor
  multi-author bronnen en is al de defacto standaard in 97 entries.
- **Implicatie als L2-praktijk wint**: Fase 0 entries hernoemen naar
  lowercase + multi-author-stijl; promote_reference.py regex versoepelen
  naar `^REF_[A-Za-z][A-Za-z0-9_-]*_\d{4}[a-z]?$`; protocol §6.2
  voorbeeld bijwerken.

### 2. D1 hoort bij L1/C1 (Fase 3), niet bij L2 (Fase 1)

- D1's schema heeft géén `ref_id` en géén `authors[]` — het gebruikt
  `id` (LNNN), `apa7` (full string) en `authors_raw` (full string).
- De aanname dat L2 + D1 schema-compatibel waren leek logisch (vergelijk-
  bare bestandsnaam) maar klopt niet.
- Run van `find_shared_refs.py` op L2 ↔ D1 leverde 0 exacte matches en
  0 fuzzy matches op (omdat D1 geen `authors[].family` heeft).
- Een ad-hoc parser op `authors_raw` vond slechts 2 overlappingen op
  (familienaam, jaar): `crane 2015` en `scheerder 2011`. Vermoedelijk
  ondertelling — bv. Deci/Ryan (L2 eerste auteur Deci) vs Ryan/Deci
  (D1 eerste auteur Ryan) wordt gemist door volgorde-verschil.
- **Implicatie**: D1 verschuift in het oorspronkelijke plan van Fase 1
  naar Fase 3 (samen met L1 en C1). Fase 1 wordt effectief
  "L2-pure-promotion".

### 3. Architecturele kandidaten al gedeeltelijk in L2 aanwezig

Op basis van auteur-match in L2:

| Architecturele kandidaat | In L2? | L2 ref_id |
|---|---|---|
| Sterman 2000 | ✓ | `REF_sterman_2000` |
| Edmondson 1999 | ✓ | `REF_edmondson_1999` |
| Schein 2010 | ✓ | `REF_schein_2010` |
| Deci & Ryan 2000 | ✓ | `REF_deci_ryan_2000` |
| Edmondson 2019 | extra | `REF_edmondson_2019` |
| Teece 2007 | ✗ | — |
| Bronfenbrenner 1979 | ✗ | — |
| Coleman 1988 | ✗ | — |
| Kozlowski & Klein 2000 | ✗ | — |

Voor de eerste 4: L2 is "tweede" gebruiker (na A_ als architectuur-
fundament) → governance-trigger voor promotie. `used_by` mag dan
`["A_", "L2"]` zijn. Voor de overige 4: alleen `["A_"]`.

---

## Generiek schema voorstel

Doel: één schema dat per model **uitbreidbaar** is met model-specifieke
velden zonder dat de gedeelde kern divergeert. Velden in drie lagen:

### Verplichte kern (alle modellen)

| Veld | Type | Toelichting |
|---|---|---|
| `ref_id` | string | Format `REF_<eerste-auteur-fam-lower>_<jaar>[suffix]`; conventie volgt L2-praktijk (zie kritiek punt 1) |
| `authors` | `array<{family: str, given: str}>` | CSL-JSON convention; consistent met L2/A_ |
| `year` | integer | |
| `title` | string | |
| `type` | string (enum) | `journal_article`, `book`, `book_chapter`, `report`, `conference_paper`, `web_resource`, `other` |
| `evidence_class` | string (enum) | `A`/`B`/`C`; mag `null` voor onbekend |

### Optionele bibliografische velden

| Veld | Type | Toelichting |
|---|---|---|
| `cite_key` | string | Korte BibTeX-stijl key |
| `source` | string | Journal-naam of publisher |
| `volume`, `issue`, `pages` | string | |
| `doi` | string | |
| `url` | string | |
| `apa_citation` | string | Volledige APA-versie als convenience-veld; redundant maar handig |
| `edition`, `editors`, `publisher` | string | Voor boeken |
| `abstract_summary` | string | Korte abstract |

### Lokale model-velden (mogen eigen vorm houden)

Niet harmoniseren — hier mag elk model zijn eigen structuur:

- L2: `avv_usage[{file, context, element_id, usage_type}]`
- L3: `themas[int]`, `kernconcepten[str]`, `categorie`, `niveau`
- D1: `refs_nodes[]`, `refs_edges[]`, `domain`, `theme`, `status`
- L1: `node_refs[]`, `domain`, `kernthema`
- C1: nog niet bestaand

Aanbevolen container: `usage` (object) of model-prefixed
(`avv_usage`, `sdm_usage`, etc.) — beide werkt, mits stripping in
`promote_reference.py` consistent.

### Gedeeld-register-additions (alleen in `A_/literatuur/gedeeld_register.json`)

| Veld | Type | Toelichting |
|---|---|---|
| `used_by` | `array<string>` | Modelprefixen die de bron gebruiken |
| `concepts` | `array<string>` | Architecturele concepten |
| `deprecated` | boolean | + reden in `verification_notes` |
| `verification_notes` | string | |

### Status / verificatie

| Veld | Type | Toelichting |
|---|---|---|
| `verified` | boolean | Bibliografisch geverifieerd door eigenaar |
| `verification_notes` | string | Tekst over status / openstaande controle |

### Mapping per model — wat moet er waar komen

**L2**: vrijwel conform. Toevoegen: `evidence_class` (kan afgeleid van
`tags` of als nieuwe kolom). `avv_usage` → `usage` of behouden.

**L3**: substantieel werk. Toevoegen: `ref_id` (afleiden uit `auteurs` +
`jaar`), `authors[{family, given}]` (parse `auteurs`-string), `title`
(= `titel`). Behouden: `lit_id` (interne stabiele key), `apa_citation`,
`themas`, `kernconcepten`, `categorie`, `niveau` (= `evidence_class`).
Mapping: `niveau` → `evidence_class` 1-op-1.

**D1**: substantieel werk. Toevoegen: `ref_id` (afleiden uit `authors_raw`
+ `year`), `authors[{family, given}]` (parse `authors_raw`), `title`
(parse uit `apa7`), `evidence_class` (= `status`, met `-` → `null`).
Behouden: `id`, `apa7`, `authors_raw`, `refs_nodes`, `refs_edges`,
`domain`, `theme`. Mapping: `status` → `evidence_class` 1-op-1.

**L1**: complete restructure markdown → JSON. Per rij van de tabel:
parse APA-citatie voor auteurs/jaar/titel, behoud kolommen Type/
Referenties/Domein/Kernthema/Status/Herkomst als `usage` of legacy-
velden.

**C1**: complete restructure markdown → JSON. Inline citations
extraheren is geen routine-werk — apart story / domein-expert-input.

**A_**: skeleton al passend bij voorgesteld schema. Optioneel-veld-
markeringen nog netjes documenteren.

---

## Reeds geleverd (te kopiëren uit `graaf_zeppelin`)

Branch in graaf_zeppelin: `claude/import-action-plan-MbUvy`.
Al deze bestanden staan in de root van die branch.

| Bron in graaf_zeppelin | Bestemming in atlas |
|---|---|
| `atlas-fase0-gedeeld-register.json` | `A_Modulaire Modelarchitectuur/literatuur/gedeeld_register.json` (overschrijft skeleton) |
| `atlas-fase0/promote_reference.py` | `_scripts/promote_reference.py` |
| `atlas-fase0/paths.yml` | `_scripts/paths.yml` |
| `atlas-fase0/README.md` | tot Fase 0-werk in atlas-stories of laat los staan |
| `atlas-fase1/find_shared_refs.py` | `_scripts/find_shared_refs.py` |
| `atlas-fase1/README.md` | tot Fase 1-werk |
| `atlas-controle-25apr2026.md` | optioneel — `docs/atlas-controle-25apr2026.md` als feedback-archief |

**Belangrijke kanttekening bij `atlas-fase0-gedeeld-register.json`**:
de 8 entries gebruiken hoofdletter-style `ref_id` (`REF_Edmondson_1999`).
Als de keuze valt op L2-praktijk (lowercase, multi-author met `_`),
hernoemen naar `REF_edmondson_1999`, `REF_deci_ryan_2000`, etc. vóór
plaatsing. Zie kritiek punt 1.

**Belangrijke kanttekening bij `paths.yml`**: de paden gaan ervan uit dat
L1 en C1 een `<MODEL>_referenties.json` krijgen. Die bestaan nog niet
(L1+C1 zijn markdown). Tot Fase 3 is uitgevoerd geven die paden
"bestand niet gevonden"-warnings — geen blokkade, alleen niet-werkende
modellen voor cross-model promotie.

---

## Aanbevolen vervolg (in deze volgorde)

**Stap 0 — beslissingen vooraf** (geen werk, wel afspraak nodig):

1. **ref_id-conventie**: kies tussen protocol-stijl (hoofdletter) en
   L2-praktijk (lowercase, multi-author). Aanbeveling: L2-praktijk
   omdat 97 entries al die kant op staan en het natuurlijker is voor
   multi-author. Werk dat eruit volgt: protocol §6.2 voorbeeld
   bijwerken; Fase 0 batch hernoemen; promote_reference.py regex
   versoepelen.

2. **Generiek schema**: bevestig of het voorstel hierboven werkt.
   Eventueel kleine aanpassingen (bv. wel/geen verplicht
   `evidence_class`).

**Stap 1 — Fase 0 in atlas plaatsen** (½ dag):

1. Plaats deliverables zoals tabel hierboven aangeeft.
2. Pas `gedeeld_register.json` aan op gekozen ref_id-conventie.
3. Test: `python _scripts/promote_reference.py REF_<x> --from L2 --dry-run`
   om de tool te valideren tegen echte data.
4. Commit als één batch.

**Stap 2 — L2 → gedeeld register voor de 4 reeds-aanwezige
architecturele bronnen** (½ dag):

Voor Sterman, Edmondson, Schein, Deci-Ryan: pas `gedeeld_register.json`
aan zodat hun `used_by` `["A_", "L2"]` is in plaats van `["A_"]`. En
markeer in `AVV_D1_referenties.json` `shared: true` voor deze 4 entries.
Kan met `promote_reference.py` of handmatig (4 entries).

**Stap 3 — schema-harmonisatie L3 + D1** (2-3 dagen elk, parallel
uitvoerbaar):

Per model:
- Voeg `ref_id` toe (afleiden uit auteurs + jaar; `LIT_001` →
  `REF_fogg_2009`).
- Voeg `authors[{family, given}]` toe (parse `auteurs` resp.
  `authors_raw`).
- Voeg `title` toe waar nodig (D1: parse uit `apa7`).
- Voeg `evidence_class` toe (mapping: L3 `niveau` → `evidence_class`,
  D1 `status` → `evidence_class`).
- Behoud bestaande velden (geen breaking changes).
- Test: draai `find_shared_refs.py` opnieuw — verwacht meer matches.

**Stap 4 — L2 ↔ L3 ↔ D1 cross-model batch** (1 dag):

Met geharmoniseerde registers: draai `find_shared_refs.py` op alle
3 paren (L2↔L3, L2↔D1, L3↔D1). Promoveer exacte matches met
`promote_reference.py`. Beoordeel fuzzy kandidaten handmatig.

**Stap 5 — L1 markdown → JSON** (2-3 dagen):

Schrijf parser voor de markdown-tabel in `MO 0.09 Literatuuroverzicht
Vermogensmodel.md`. Output: `L1_referenties.json` in voorgestelde
schema. Dan: cross-model overlap tegen L2/L3/D1.

**Stap 6 — C1 markdown → JSON** (langer, vereist domein-input):

Inline citations extraheren uit narrative essay. Geen routinewerk.
Mogelijk: handmatige catalogisering door C1-eigenaar, of NLP-extractie
als startpunt + handmatige cleanup.

---

## Tips voor de agent in atlas-repo

- **De bestaande tooling werkt op `paths.yml`**. Bij folder-rename uit
  de harmonisatie (`A_/docs/dwarsdoorsnede_modellenstructuur.md`) hoef
  je alleen `paths.yml` aan te passen.
- **Test elke promotie eerst met `--dry-run`**. Het script schrijft
  ook lokaal `shared: true` — niet wenselijk in een test.
- **De governance-regel** (twee modellen → promotie) is een
  *waarschuwing*, geen blokkade. Voor architecturele bronnen wordt de
  warning automatisch overgeslagen als `--from A_` wordt gebruikt.
- **`find_shared_refs.py` schrijft alleen naar zijn `--out` rapport**,
  nooit naar de registers — veilig om regelmatig te draaien.
- **Bij schema-conflicten**: voorstel in deze instructie gaat uit van
  niet-breaking uitbreidingen. Bestaande velden behouden, nieuwe velden
  ernaast plaatsen.

---

## Snel-referentie: ad-hoc overlap-check via `authors_raw` parse

Als je tussentijds wil weten welke L2-bronnen overlap hebben met
D1 (zonder D1 te harmoniseren):

```python
import json, re
l2 = json.load(open("L2_.../literatuur/AVV_D1_referenties.json"))
d1 = json.load(open("D1_.../literatuur/SDM_D1_referenties.json"))
def norm(s): return re.sub(r"[^a-z]", "", s.lower())
l2_keys = {(norm(e["authors"][0]["family"]), e["year"]): e["ref_id"]
           for e in l2["references"] if e.get("authors") and e.get("year")}
d1_keys = {(norm(e["authors_raw"].split(",")[0]), e["year"]): e["id"]
           for e in d1["references"] if e.get("authors_raw") and e.get("year")}
overlap = set(l2_keys) & set(d1_keys)
for k in sorted(overlap):
    print(f"{k} — L2: {l2_keys[k]} | D1: {d1_keys[k]}")
```

Dit gaf op 26 april 2026: 2 overlap-paren (`crane 2015`, `scheerder 2011`).
Verwacht ondertelling door auteur-volgorde-verschillen.

---

## Open vragen die in de nieuwe sessie nog beslist moeten worden

1. ref_id-conventie (zie kritiek punt 1).
2. Wel of niet `evidence_class` verplicht in gedeeld register?
3. `usage`-veld of model-prefixed (`avv_usage`, etc.) voor lokale
   model-velden?
4. Hoe wordt L3's `categorie`-veld (237 unieke vrije waardes) gemapt
   naar het uniforme `type`-enum?
5. Wordt C1's narrative essay handmatig naar JSON gebracht, of via
   NLP-extractie als startpunt?

---

*Einde instructie. Veel succes in atlas — alle voorbereidende analyse
ligt klaar; het is voornamelijk plaatsen + beslissingen + uitvoering.*

