# Uniforme kenmerken-taxonomie voor graph-objecten

**Status:** Wens / vision doc
**Scope:** cross-project — Graaf Zeppelin, Codebase-Olympus, toekomstige graph-projecten
**Aanleiding:** gesprek bij S14-05 (ID-schema herontwerp), 23 april 2026

## De observatie

Een graph-object — zowel een **node** als een **edge** — draagt in de praktijk twee
soorten kenmerken:

1. **Generieke kenmerken**, bepaald door het type graaf (DAG, causale DAG,
   semantisch netwerk, systeem-dynamica-model, ...). Voorbeelden bij causale DAGs:
   `id`, `label`, `domain`, `level` (op nodes); `source`, `target`, `polarity`,
   `strength`, `edge_type`, `base_weight` (op edges).
2. **Specifieke kenmerken**, bepaald door het onderwerp van de graaf (sportdeelname,
   vitale vereniging, gezondheidszorg, ...). Voorbeelden bij sportdeelname:
   `disciplines`, `slider_sensitivity`, `bond_influence`.

Nu groeit elk project zijn eigen veld-set min of meer onafhankelijk. Graaf Zeppelin
heeft 12 edge-velden; Olympus' vergelijkbare graphs hebben een andere set. Sommige
velden overlappen inhoudelijk maar heten anders; sommige heten hetzelfde maar
betekenen subtiel iets anders; sommige zijn "domein-specifiek" genoemd maar zouden
op elk causaal netwerk nuttig zijn.

Dit levert drie problemen:

- **Drift tussen projecten.** Een review-checklist of invariant-bibliotheek in
  project A werkt niet schoon op project B — niet omdat de graphs wezenlijk
  verschillen, maar omdat de veldnamen uit elkaar lopen.
- **Onduidelijkheid voor reviewers en LLM-tools.** Welke velden mag je aannemen
  als "altijd aanwezig op een causale DAG"? Daar bestaat nu geen gedeelde definitie
  van.
- **Ad-hoc keuzes blijven hangen.** Een veld dat ooit voor één use-case is
  toegevoegd (zoals Zeppelin's `slider_sensitivity`) wordt niet heroverwogen
  wanneer een ander project dezelfde informatie anders modelleert.

## De wens

Over meerdere projecten heen, nog een keer zitten om te komen tot:

> **Per graph-type een werkende set kenmerken: uniform waar het kan, specifiek waar
> het moet — voor zowel nodes als edges.**

Concreet wil dat zeggen:

- **Een kern-schema per graph-type**, bindend voor elk project dat dat type claimt
  te gebruiken. Een "causale DAG" in project X en Y heeft dezelfde kernvelden,
  dezelfde enum-waardes, dezelfde semantiek.
- **Een expliciet uitbreidingspunt voor project-specifieke velden**, duidelijk
  gescheiden van de kern. Bijvoorbeeld een `extras`/`metadata`-subobject of
  een naamruimte-conventie (`sport.slider_sensitivity` vs `kern.base_weight`).
- **Dezelfde behandeling voor nodes en edges.** Beide zijn graph-objecten en
  dezelfde taxonomie-aanpak geldt voor beide — kern-kenmerken horen aan de
  graph-typedefinitie vast te zitten; onderwerp-specifieke kenmerken horen in een
  heldere uitbreidingszone.
- **Verankerd in de methodologie** (Olympus' `docs/graph-methodology.md`), niet
  alleen in losse project-docs.

Dit is geen haastklus; het vereist een gesprek met minimaal één ander
graph-project (Olympus) en ideaal een korte rondgang langs lopende of recente
use-cases (sportdeelname, vitale vereniging, eventuele andere Olympus-domeinen)
om de huidige veld-sets naast elkaar te leggen.

## Hoe dit raakt aan EPIC-14

EPIC-14 doet drie dingen die de voorbereiding van deze taxonomie versnellen — maar
probeert zelf niet die taxonomie vast te leggen:

- **S14-02 (Pydantic-modellen)** introduceert een expliciet `Graph`/`Node`/`Edge`-
  model met StrEnums. Dat is de natuurlijke plek waar kern vs. specifiek later
  formeel vastgeklikt wordt. S14-02 legt de **structuur** aan; de cross-project
  overeenkomst over **inhoud** volgt later.
- **S14-04 (invarianten-catalogus)** maakt zichtbaar welke checks graph-agnostisch
  zijn (cycles, orphans, duplicates, dangling refs, weight-range) — exact de
  set die in het kern-schema hoort thuis te horen.
- **S14-05 (ID-schema)** is het eerste concrete experiment met een gestandaardiseerde
  naamconventie. Vorm A (`UIT-L0-001`) hangt af van de `domain`+`level`-taxonomie;
  als die bij cross-project overleg uniformer wordt, moet Zeppelin's ID-schema
  eventueel meebewegen. Vandaar dat de mapping-file uit S14-05 bewaard blijft
  (`data/migrations/old_to_new_ids.json`).

## Opvolging

Dit doc is nadrukkelijk geen actieplan — het is een **wens** die op de juiste plek
moet landen. Mogelijke volgende stappen, op volgorde van wat het meest nuttig is:

1. **Bespreken in Olympus-conversatie.** Aan het eind van S14-02 (of eerder als
   het natuurlijk valt), deze notitie als discussie-stuk inbrengen bij Olympus.
2. **Naast-elkaar-schema-analyse.** Zeppelin's 12 edge-velden + node-velden naast
   Olympus' vergelijkbare graphs leggen; drie kolommen: overlappend/anders-genoemd,
   project-specifiek-met-reden, project-specifiek-zonder-reden.
3. **Vastleggen in methodologie.** Het resultaat hoort thuis in Olympus'
   `docs/graph-methodology.md` (als uitbreiding op §1 Pydantic-typen of als
   nieuwe §9), niet alleen in project-docs.
4. **Pas daarna**: Zeppelin's Pydantic-model aligneren (eventueel een S14-02-
   vervolgstory) en Olympus dat ook doen.

## Niet-scope (om de wens scherp te houden)

- Geen monorepo, geen gedeelde Python-package van typen. De methodologie is
  gedeeld; de codebase blijft per project.
- Geen poging om de taxonomie nu al vast te leggen. Dat gebeurt in een later
  gesprek met minstens twee projecten op tafel.
- Geen nieuwe veldnamen uitvinden vooruitlopend op dat gesprek. Binnen EPIC-14
  volgen we de bestaande Zeppelin-velden; alleen de ID-vorm wordt aangepast.

---

**Eigenaar van de opvolging:** Max, in de Olympus-conversatie. Dit doc kan ook
als basis voor een issue in `maxonamission/Codebase-Olympus` wanneer dat
opportuun is.
