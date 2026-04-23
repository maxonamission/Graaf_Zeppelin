# Schema-evolutie v1 → v2 — een migratie-voorbeeld

**Status:** Bijdrage aan de cross-project graph-methodologie (S14-07).
**Doelgroep:** andere graph-projecten (Codebase-Olympus, toekomstige
varianten) die voor dezelfde schema-sprong staan.
**Cross-reference:** zie `docs/uniforme-kenmerken-taxonomie.md` voor de
bredere wens om graph-object-kenmerken cross-project te uniformeren.

Graaf Zeppelin is van een minimaal v1-schema doorgegroeid naar een
rijker v2-schema zonder die overgang in één big-bang-migratie te
doorlopen. Dit document beschrijft wat er is veranderd, hoe het is
uitgevoerd, en wat we de volgende keer anders zouden doen.

## Waarom v2 nodig was

Het v1-schema was gebouwd rond één directe vraag: *"welke factor
beïnvloedt welke andere, en hoe sterk?"* Dat gaf een verrassend nuttig
15-knopen-model (`data/models/sportdeelname_v1.json`), maar het schema
kwam al snel in de knel toen het product volwassener werd:

- **Geen domeinstructuur.** Alle factoren stonden naast elkaar zonder
  groepering. Niet-technische gebruikers konden de graaf niet
  overzichtelijk navigeren, en er was geen manier om filters "toon
  alleen psychologische factoren" te bouwen.
- **Geen edge-types.** Elke `relation` was een generieke pijl met
  `direction`, `strength` en `description`. Onderscheid tussen
  *structural* (eenrichting-oorzakelijk), *mediating* (via-via),
  *moderator* (versterkt/verzwakt een andere edge), *feedback*
  (terugkoppeling) en *social_regulatory* (sociale druk over en weer)
  bestond niet — waardoor cycle-detectie een brute keuze was tussen
  "alles mag" of "niets mag".
- **Geen beleidssliders.** Het product wil beleidsmedewerkers laten
  simuleren "wat als we meer investeren in coaching?". Dat vereist
  interventie-knoppen die een aantal edges tegelijk moduleren. In
  v1 was zoiets alleen via ad-hoc code mogelijk.
- **Geen curve-functies.** `strength: 0.9` is prima voor een lineaire
  werking, maar sommige mechanismen hebben een drempel
  (`DAMPENING_THRESHOLD`), een optimum (`INVERTED_U`) of een logistische
  vorm (`THRESHOLD_LOGISTIC`). Zonder `curve_type + curve_params` was
  dat niet te modelleren.
- **Geen bronverwijzing.** Elke edge in v2 heeft `literature: [L053,
  L054, ...]`. In v1 was een causale relatie een blind getal; het was
  onmogelijk om bij een review te checken op welke wetenschap die 0.9
  gebaseerd was.
- **Geen metadata-laag.** v1 had slechts `name`, `version`,
  `description` bovenaan. v2 heeft een volledige `metadata`-blok met
  `deliverable`, `project`, `domain_name`, `language`, `persona`,
  `example_questions`, `sources`, `summary` en `graph_metrics`. Dat is
  wat S12-06 later domein-agnostisch maakte: dezelfde app kan met een
  ander v2-bestand een heel andere taal en persona tonen zonder
  codewijziging.

Kort gezegd: v1 was "de tekening op de achterkant van een bierviltje"
en v2 is "het modelleer-schema waar een beleidsverkenner echt op kan
draaien".

## Wat concreet veranderde

### Top-level structuur

| v1 | v2 |
|---|---|
| `name` | → verhuisd naar `metadata.project` + `metadata.domain_name` |
| `version` | → `metadata.version` |
| `description` | → `metadata.summary.description` |
| `factors` (15) | → `nodes` (69) |
| `relations` (26) | → `edges` (114) |
| — | `sliders` (8 beleidssliders, compleet nieuw) |
| — | `metadata` (rijk blok met persona, example_questions, sources, graph_metrics) |

### Nodes: van 4 velden naar 11

v1-factor had alleen `id`, `label`, `description`, `category`. v2-node
heeft daarnaast:

- **`domain`** (9 waardes: *Uitkomsten, Regels & Administratie, Sociaal,
  Psychologisch, Middelen & Logistiek, Organisatie & Aanbod, Training
  & Prestatie, Macro-context, Discipline-specifiek*) — semantische
  groepering.
- **`level`** (`L0`/`L1`/`L1/L2`/`L2`/`L3`) — afstand tot de uitkomst.
  `L0` = de uitkomst zelf, `L3` = macro-context.
- **`definition`** — uitgebreidere beschrijving dan `description`.
  In de code behandelen we ze als synoniemen.
- **`bond_influence`** (`high`/`medium`/`low`/`none`) — hoeveel invloed
  een sportbond op deze factor heeft. Sport-specifiek.
- **`disciplines`** (lijst) — welke sportdisciplines de node betreft.
- **`status`** (`A`/`B`/`-`) — validatie-niveau van de curatoren.
- **`degree`**, **`in_degree`**, **`out_degree`** — afgeleide graph-
  metrics, in de JSON ingevroren (met de bekende drift-risico, zie
  "Lessen").

### Edges: van 5 velden naar 19 (uiteindelijk 18)

v1-relation had `cause`, `effect`, `direction`, `strength`,
`description`. v2-edge voegde toe:

- **Rijkere identificatie**: expliciete `id`, `source_label` en
  `target_label` voor snelle menselijke herkenning zonder node-lookup.
- **`target_type`** (`node`/`edge`) — edges kunnen nu ook **andere
  edges** als target hebben: moderator-edges. Dit is de grootste
  structurele verandering; zie verderop.
- **`polarity`** (NL: `positief`/`negatief`/`variabel`/`moderator`)
  vervangt v1's `direction` (EN: `positive`/`negative`/`variable`). De
  loader accepteert beide vormen (S12-05 meertaligheid).
- **`strength`** ging van **numeriek** (`0.9`) naar **categorisch**
  (`sterk`/`midden`/`zwak`). Om geen precisie te verliezen is er ook
  een numeriek veld `base_weight` (0.0–1.0) bijgekomen; de loader
  gebruikt dat als de primaire bron en valt terug op een mapping van
  het label wanneer `base_weight` ontbreekt.
- **`edge_type`** (`STRUCTURAL`/`MEDIATING`/`MODERATOR`/`FEEDBACK`/
  `SOCIAL_REGULATORY`) — essentieel voor de per-edge-type-cycle-check
  die S14-01 introduceerde.
- **`curve_type` + `curve_params`** (`LINEAR`/`INVERTED_U`/
  `THRESHOLD_LOGISTIC`) — niet-lineaire mechanismen modelleren.
- **`cluster`** — los van `domain`; een operationele groepering
  (bv. "Toelaatbaarheid") waar sliders op richten.
- **`bond_influence`, `disciplines`, `status`** (identiek aan nodes).
- **`literature`** — lijst van bron-IDs (`[L053, L054, L056]`).
- **`mechanism`** — vrije tekst die het mechanisme beschrijft.
- **`slider_sensitivity`** — dict `{sens_key → high/medium/low/none}`
  die zegt welke beleidssliders deze edge beïnvloeden en hoe sterk.
- **`time_lag`** — kwam bij v2 binnen maar is in S14-03 (Pad B) weer
  verwijderd omdat de simulatie er niets mee deed. Dat is expliciet
  op de roadmap gezet als toekomstige dynamiek-epic.

### Nieuw: sliders

Een apart top-level-concept dat in v1 niet bestond. Acht sliders
(gecontroleerd per `sensitivity_key` zoals `sens_economisch`,
`sens_accommodatie`) met elk een `curve_type`, `curve_params`,
`default`, `range`, `direction`, `related_nodes`, `primary_clusters`,
`evidence` en `qualifiers`. Die `qualifiers` zijn kwalificatievragen
die een beleidsmedewerker beantwoordt om een sliderwaarde te bepalen
zonder zelf `0.63` te hoeven tikken.

### Samengevat

v1-item → v2-item, in één getal:

- v1: 15 factoren × 4 velden + 26 relaties × 5 velden ≈ 60 + 130 = **190 datapunten**
- v2: 69 nodes × 11 velden + 114 edges × 18 velden + 8 sliders × 15 velden + metadata ≈ 759 + 2 052 + 120 + ~40 = **~2 970 datapunten**

Een factor 15 aan datadichtheid bij een factor 4-5 aan model-grootte.

## Hoe de migratie werd uitgevoerd

De migratie was geen one-shot-forward-only-script. In plaats daarvan
koos Zeppelin voor een **code-based coexistence**-aanpak:

1. **v1-data blijft staan** als historische referentie
   (`data/models/sportdeelname_v1.json`, 15 factoren / 26 relaties).
   Ze wordt niet geüpgraded; ze is een museum-exemplaar.
2. **v2-data leeft naast v1** als nieuwe file
   (`data/models/sportdeelname_graph.json`, 69 nodes / 114 edges). Het
   hele ontwikkelteam verwees zijn werk vanaf commit `57ed4f7` naar
   dit nieuwe bestand.
3. **De loader detecteert de versie** in `CausalDAG.from_dict()`: als
   de data `nodes` en `edges` heeft → v2, anders v1. Beide paden
   (`_from_dict_v1`, `_from_dict_v2`) bestaan nog steeds in
   `app/core/dag_engine.py`.
4. **Conversie op laad-tijd, niet op disk.** De loader mapt v1's
   `direction`/`strength` naar v2's `polarity`/`base_weight` tijdens
   het bouwen van de NetworkX-graaf. De JSON wordt niet aangeraakt.
5. **Tests voor beide paden blijven groen.** `test_dag_engine.py`
   heeft een `TestCausalDAGv1`-klasse die tegen v1-data draait en een
   `TestCausalDAGv2`-klasse voor v2-data. Het `test_load_sportdeelname_v1`
   blijft vereist om te garanderen dat v1-loads niet regresseren.

De prijs hiervan is dat `dag_engine.py` twee loader-paden bevat. De
winst is dat de migratie geen risicomoment had: elke commit kon
teruggedraaid worden en het oude model bleef onder alle
omstandigheden laadbaar.

## Backward compat

De backward-compat-strategie is eenvoudig: **behouden op code-niveau,
loslaten op product-niveau**.

- **App-laag** (`app/main.py`, `app/api/graph.py`, …) gebruikt alleen
  v2; alle queries, simulaties en LLM-prompts leunen op
  domain/slider/literature-velden die v1 niet heeft.
- **Loader-laag** (`CausalDAG.from_dict`) ondersteunt beide en kan dus
  een v1-model inladen — maar de app-laag zou er weinig nuttigs uit
  kunnen halen (geen domains, geen sliders, geen curves).
- **Test-laag** bewaakt beide paden zodat een onbedoelde breuk van v1
  zichtbaar is; geen nieuwe features worden voor v1 gebouwd.

Er is bewust geen migratiescript geschreven dat v1 → v2 JSON omzet. De
reden is praktisch: het nieuwe v2-model is niet een verrijkte versie
van het oude model, het is een inhoudelijk andere graaf (69 vs 15
knopen; overlappende maar niet-identieke factoren). Een geautomatiseerde
conversie zou dus op zijn best een skelet opleveren dat alsnog handmatig
met alle v2-velden ingevuld moet worden — de energie ging in plaats
daarvan rechtstreeks naar het bouwen van de nieuwe graaf.

## Schema-evolutie gaat door — EPIC-14 tweaks

v2 was niet het eindpunt. EPIC-14 (actieplan vanuit Codebase-Olympus)
heeft het v2-schema verder gedisciplineerd zonder de versie-letter op
te hogen:

- **S14-01** — cycle-detectie per `edge_type` in plaats van globaal.
  `FEEDBACK`- en `SOCIAL_REGULATORY`-edges mogen nu cyclisch zijn,
  wat het schema altijd al suggereerde maar de code eerder afwees.
- **S14-02** — Pydantic-modellen (`app/core/graph_models.py`) als
  canonieke schema-poort. Validatie gebeurt nu bij laden, niet bij
  gebruik; een enum-fout of dangling reference komt als één
  `ValidationError` naar boven in plaats van een late-binding
  `KeyError`.
- **S14-03** — `time_lag` verwijderd uit het schema. Het veld werd
  opgeslagen maar door de simulatie niet gebruikt ("dead field
  anti-pattern"). Her-activeren (iteratieve-tik-simulatie) is op de
  roadmap gezet in `PLAN.md`.
- **S14-04** — invarianten-catalogus (`app/core/validation.py`) die
  cycles, orphans, duplicates, dangling refs, connectivity en
  edge-weight-ranges in één `ValidationReport` bundelt. CLI op
  `scripts/validate_graph.py`.
- **S14-05** — ID-schema integrale migratie van opaak (`N001`/`E001`)
  naar leesbaar (`UIT-L0-001`/`E-MED-014`). Mapping-file bewaard in
  `data/migrations/old_to_new_ids.json`. Zie `docs/id-schema.md`.

Deze wijzigingen zijn niet als v3 gelabeld omdat ze individueel en
achtereenvolgens zijn doorgevoerd, met de Pydantic-laag als garantie
dat de cumulatieve vorm consistent bleef. Of er ooit een v3 komt hangt
af van de cross-project-taxonomie-gesprekken (zie
`docs/uniforme-kenmerken-taxonomie.md`); voorlopig blijft het v2 met
expliciete evolutie-trail in deze secties.

## Lessen — wat zouden we anders doen?

1. **Schema-versie als first-class metadata.** v2 heeft `version:
   2.3.0` in `metadata` — dat is goud waard. Loader-routing op
   structuurdetectie (aanwezigheid van `nodes`/`edges`) werkte maar is
   fragieler dan een expliciete versie-check. Een volgend nieuw
   project zou meteen `schema_version: 2` als verplicht top-level-veld
   neerzetten.
2. **Afgeleide velden horen niet in de data.** Nodes hebben `degree`,
   `in_degree`, `out_degree` in de JSON. Die kunnen drift krijgen
   ten opzichte van de echte NetworkX-structuur (bijvoorbeeld na het
   toevoegen van een edge zonder de metadata te herberekenen). S14-04's
   validator ontdekte dit stilletjes op `N066`/`PSY-L1-011` dat zich
   gedroeg als orphan in de NetworkX-view maar `out_degree: 1` claimde
   in de data. Conclusie: bewaar *brongegevens* in de data, niet
   *afleidingen*.
3. **Lege strings op optionele enum-velden zijn een Pydantic-vijand.**
   v2 gebruikt `"time_lag": ""`, `"curve_type": ""` voor "niet
   ingevuld". Prima in een dict-based wereld, maar zodra Pydantic in
   beeld komt moet elk zo'n veld door een `_empty_to_none`-validator.
   Een volgend schema zou `null` gebruiken, niet `""`.
4. **Moderator-edges als `target_type=edge` zijn elegant maar duur.**
   Ze vallen buiten de gewone NetworkX-graaf — wat betekent dat
   standaard graph-algoritmes (orphan-check, connected components) een
   vals-positief geven op knopen die alleen via moderator-relaties
   deelnemen. De workaround in `find_orphan_nodes` is een
   `extra_participating_ids`-parameter. Een alternatief had kunnen zijn
   om moderators als knoop-attribuut ("modereert edge X") te modelleren
   in plaats van als edge-naar-edge. Trade-off, bewust geaccepteerd.
5. **Een migratiescript is niet altijd het goede antwoord.** Voor de
   v1→v2-sprong was geautomatiseerde conversie zinloos omdat het
   nieuwe model een grotere, rijkere graaf was. Voor de latere
   S14-03 (`time_lag`) en S14-05 (ID-schema) waren idempotente
   scripts exact het juiste gereedschap. Het type migratie bepaalt de
   aanpak, niet het feit-dat-het-een-migratie-is.
6. **Coexistence-aanpak heeft lange houdbaarheid.** De `_from_dict_v1`-
   branch in `dag_engine.py` bestaat nu meer dan twee jaar en kost
   ~30 regels. Dat is cheap insurance en geeft test-discipline omdat
   v1-tests niet stuk mogen.

## Cross-reference naar Olympus

Dit document is geschreven als bijdrage aan de gedeelde graph-
methodologie van Codebase-Olympus. Voorgestelde haak: voeg in
`docs/graph-methodology.md` §3 ("Lean JSON + content separation") een
verwijzing toe:

> Een uitgewerkt voorbeeld van schema-evolutie in de praktijk — inclusief
> coexistence-aanpak, latere disciplinering via een Pydantic-laag, en
> lessen over afgeleide-velden-drift — staat in
> [Graaf Zeppelin `docs/schema-evolution.md`](https://github.com/maxonamission/Graaf_Zeppelin/blob/main/docs/schema-evolution.md).

De Olympus-repo zelf ligt buiten de scope van deze story; de
cross-reference-PR is een eigen kleine taak in de Olympus-conversatie.

## Scope — wat dit doc niet is

- Geen migratiehandleiding voor andere projecten. Elk graph-project heeft
  eigen context; de lessen hierboven zijn suggesties, geen voorschriften.
- Geen roadmap. Latere schema-wijzigingen horen in `PLAN.md` en in
  eigen stories onder `stories/`, niet hier.
- Geen poging om de uniforme kenmerken-taxonomie vast te leggen. Dat
  vereist een cross-project gesprek; zie het eigen doc daarvoor.
