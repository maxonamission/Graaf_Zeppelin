# ID-schema

**Status:** Bindend vanaf S14-05 (EPIC-14).
**Code:** `app/core/id_schema.py` is de canonieke bron; deze pagina is de
menselijke referentie.
**Migratie-audit:** `data/migrations/old_to_new_ids.json` bewaart de
mapping van de oude opake IDs (`N001`/`E001`) naar het nieuwe schema.

## Waarom

Opake IDs (`N001`, `E002`) zeggen niets over wat een node of edge *is*.
Een diff, review of beleidsgesprek moet naar de datatabel om te zien dat
`N034` "Reiskosten" is. Met een hiërarchisch leesbaar ID staat die
informatie **in het ID zelf**: `MDL-L1-006` is meteen herkenbaar als een
L1-node in "Middelen & Logistiek".

## Vorm (Vorm A uit het actieplan)

```
Nodes:  {DOMEIN-AFK}-{NIVEAU}-{VOLGNR}
        UIT-L0-001     Uitkomsten, L0, volgnr 001
        TRP-L1-012     Training & Prestatie, L1, volgnr 012
        SOC-L12-005    Sociaal, L1/L2 (→ L12), volgnr 005

Edges:  E-{EDGE_TYPE_AFK}-{VOLGNR}
        E-MED-014      MEDIATING, volgnr 014
        E-FBK-007      FEEDBACK, volgnr 007
```

- Volgnr is altijd 3-cijfer zero-padded (`001`, `012`, `100`).
- Volgnrs lopen **per bucket**: voor nodes binnen `{DOMEIN, NIVEAU}`,
  voor edges binnen `{EDGE_TYPE}`. Geen globale nummering.
- Edge-IDs gebruiken bewust de EN-afkorting van de `edge_type`-enum;
  node-IDs gebruiken de NL-domein-afkorting. Die asymmetrie is
  verdedigbaar: edges zijn technisch, knopen zijn domein-inhoud.

## Domein-afkortingen

| Domein                  | Afk.  |
|-------------------------|-------|
| Uitkomsten              | `UIT` |
| Regels & Administratie  | `REG` |
| Sociaal                 | `SOC` |
| Psychologisch           | `PSY` |
| Middelen & Logistiek    | `MDL` |
| Organisatie & Aanbod    | `ORG` |
| Training & Prestatie    | `TRP` |
| Macro-context           | `MAC` |
| Discipline-specifiek    | `DIS` |

## Edge-type-afkortingen

| Edge-type           | Afk.    |
|---------------------|---------|
| `STRUCTURAL`        | `STR`   |
| `MEDIATING`         | `MED`   |
| `MODERATOR`         | `MOD`   |
| `FEEDBACK`          | `FBK`   |
| `SOCIAL_REGULATORY` | `SREG`  |

## Niveau-normalisatie

Het data-niveau `L1/L2` bevat een schuine streep die ongunstig is in
een ID. In het ID-segment wordt dit genormaliseerd tot `L12`. Het
oorspronkelijke `level`-veld op de node blijft ongewijzigd (`"L1/L2"`)
— de ID is een afgeleide weergave, geen vervanging.

| Data-level | ID-level |
|------------|----------|
| `L0`       | `L0`     |
| `L1`       | `L1`     |
| `L1/L2`    | `L12`    |
| `L2`       | `L2`     |
| `L3`       | `L3`     |

## Reservering voor latere uitbreiding

Voeg je nieuwe nodes toe aan een bestaande `{DOMEIN, NIVEAU}`-bucket?
Gebruik volgnrs vanaf **100** om een eventuele collision met de
oorspronkelijke data uit te sluiten. De sportdeelname-migratie liet
alle buckets ver onder 100, dus 100+ is veilig.

## Valideren en parsen in code

```python
from app.core.id_schema import (
    validate_node_id,
    validate_edge_id,
    parse_node_id,
    parse_edge_id,
    derive_node_id,
    derive_edge_id,
)

validate_node_id("UIT-L0-001")          # True
validate_node_id("N001")                # False

parse_node_id("TRP-L1-012")
# NodeIdParts(domain_abbr='TRP', domain='Training & Prestatie',
#             level='L1', seq=12)

derive_node_id("Sociaal", "L1/L2", 5)   # 'SOC-L12-005'
derive_edge_id("FEEDBACK", 7)           # 'E-FBK-007'
```

De Pydantic-modellen in `app/core/graph_models.py` leunen op deze
helpers voor hun ID-validatie: Node-IDs moeten altijd aan het schema
voldoen; Edge-IDs mogen leeg zijn, maar als ze gevuld zijn moeten ze
het edge-schema matchen.

## Nieuwe domeinen / edge-types toevoegen

De tabellen in `DOMAIN_ABBR` en `EDGE_TYPE_ABBR` zijn bindend voor de
data onder `data/models/`. Als er ooit een nieuw domein of edge-type
komt:

1. Voeg het toe aan de betreffende tabel in `app/core/id_schema.py`.
2. Werk **deze pagina** bij.
3. Voeg een afkorting-assertion toe aan `tests/test_id_schema.py`.
4. Voeg een entry toe aan de Pydantic-enum in
   `app/core/graph_models.py` (`Polarity`/`EdgeType`/…).

## Relatie met cross-project taxonomie

Dit schema is het eerste concrete experiment met uniforme graph-object-
identifiers in Zeppelin. Het vult een hiaat dat ook voor Olympus en
toekomstige graph-projecten speelt — zie
[`uniforme-kenmerken-taxonomie.md`](uniforme-kenmerken-taxonomie.md)
voor de wens om cross-project tot een gedeelde set kenmerken te komen.
Als dat gesprek tot aanpassingen in de `domain`-of
`edge_type`-taxonomie leidt, beweegt dit ID-schema mee; de mapping-file
in `data/migrations/` is dan de steiger waarop de vervolgmigratie
bouwt.
