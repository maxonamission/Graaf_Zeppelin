#!/usr/bin/env bash
# =============================================================================
# Create GitHub Issues: Epics & Stories voor Graaf Zeppelin
#
# Gebruik:
#   gh auth login              # eenmalig inloggen
#   bash scripts/create_github_issues.sh
# =============================================================================

set -euo pipefail
REPO="maxonamission/Graaf_Zeppelin"

echo "=== Labels aanmaken ==="

gh label create "epic"            --description "High-level feature grouping"       --color "3E4B9E" --repo "$REPO" 2>/dev/null || echo "  label 'epic' bestaat al"
gh label create "story"           --description "Implementeerbare user story"       --color "0E8A16" --repo "$REPO" 2>/dev/null || echo "  label 'story' bestaat al"
gh label create "priority: high"  --description "Must have"                         --color "D93F0B" --repo "$REPO" 2>/dev/null || echo "  label 'priority: high' bestaat al"
gh label create "priority: medium" --description "Should have"                      --color "FBCA04" --repo "$REPO" 2>/dev/null || echo "  label 'priority: medium' bestaat al"
gh label create "priority: low"   --description "Nice to have"                      --color "C2E0C6" --repo "$REPO" 2>/dev/null || echo "  label 'priority: low' bestaat al"
gh label create "area: api"       --description "API endpoints"                     --color "1D76DB" --repo "$REPO" 2>/dev/null || echo "  label 'area: api' bestaat al"
gh label create "area: export"    --description "Data export / format conversion"   --color "5319E7" --repo "$REPO" 2>/dev/null || echo "  label 'area: export' bestaat al"
gh label create "area: agent"     --description "LLM agent / Copilot integration"   --color "F9D0C4" --repo "$REPO" 2>/dev/null || echo "  label 'area: agent' bestaat al"
gh label create "area: infra"     --description "Infrastructure / hosting / deploy"  --color "BFD4F2" --repo "$REPO" 2>/dev/null || echo "  label 'area: infra' bestaat al"
gh label create "fase: 2"         --description "Fase 2 - Distributie & Integratie" --color "D4C5F9" --repo "$REPO" 2>/dev/null || echo "  label 'fase: 2' bestaat al"

echo ""
echo "=== Stories aanmaken ==="

# ---------------------------------------------------------------------------
# EPIC 1 stories: TOON Export
# ---------------------------------------------------------------------------

S1=$(gh issue create --repo "$REPO" \
  --title "TOON converter: JSON graph → TOON formaat" \
  --label "story,area: export,priority: high,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beheerder van het sportdeelnamemodel
**Wil ik** de causale graph automatisch kunnen omzetten van JSON naar TOON formaat
**Zodat** LLM-gebruikers 40-50% minder tokens verbruiken bij het raadplegen van het model

## Acceptatiecriteria
- [ ] Python module `graph_to_toon.py` die `sportdeelname_graph.json` omzet naar `.toon`
- [ ] Tabular arrays voor nodes, edges, en sliders (grootste tokenbesparing)
- [ ] Metadata als geneste TOON objecten
- [ ] Moderator-edges correct gerepresenteerd (target_type: edge)
- [ ] Lossless: TOON → JSON roundtrip levert identiek resultaat
- [ ] Tokenvergelijking JSON vs TOON in CI output

## Technische notities
- TOON spec v3.0: https://github.com/toon-format/spec
- Python TOON lib: https://github.com/xaviviro/python-toon
- Graph bevat velden met komma's in labels → pipe-delimiter (`|`) overwegen
EOF
)")
echo "  Created: $S1"

S2=$(gh issue create --repo "$REPO" \
  --title "TOON export: automatisch genereren bij graph-update" \
  --label "story,area: export,area: infra,priority: medium,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beheerder
**Wil ik** dat bij elke update van de graph JSON automatisch een TOON-versie wordt gegenereerd
**Zodat** de TOON-versie altijd in sync is met de brondata

## Acceptatiecriteria
- [ ] GitHub Action / pre-commit hook die bij wijziging van `sportdeelname_graph.json` automatisch de TOON-versie regenereert
- [ ] Gegenereerd bestand: `data/models/sportdeelname_graph.toon`
- [ ] CI check: TOON-bestand is up-to-date met JSON-bron
- [ ] Versie-metadata in TOON-bestand komt overeen met JSON-bron
EOF
)")
echo "  Created: $S2"

S3=$(gh issue create --repo "$REPO" \
  --title "DOCX export: graph naar SharePoint-vriendelijk Word document" \
  --label "story,area: export,priority: medium,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** sportbondmedewerker met M365 Copilot
**Wil ik** het sportdeelnamemodel als Word-document op SharePoint hebben staan
**Zodat** Copilot het kan indexeren en ik vragen kan stellen over het causale model

## Acceptatiecriteria
- [ ] Python script dat graph JSON omzet naar gestructureerd .docx
- [ ] Secties per domein met nodes, relaties, en definities
- [ ] Moderatie-effecten apart uitgelicht
- [ ] Sliders/beleidsinstrumenten sectie
- [ ] Leesbaar voor niet-technische gebruikers
EOF
)")
echo "  Created: $S3"

# ---------------------------------------------------------------------------
# EPIC 2 stories: Graph API
# ---------------------------------------------------------------------------

S4=$(gh issue create --repo "$REPO" \
  --title "Graph API: read-only endpoints voor het causale model" \
  --label "story,area: api,priority: high,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** externe LLM-agent (Copilot, GPT, Claude)
**Wil ik** het causale model via een API kunnen bevragen
**Zodat** ik alleen relevante delen ophaal in plaats van het hele 170KB model

## Acceptatiecriteria
- [ ] `GET /api/v1/graph/metadata` — model versie, samenvatting, metrics
- [ ] `GET /api/v1/graph/nodes` — alle nodes (filter op domain, cluster, status)
- [ ] `GET /api/v1/graph/nodes/{id}` — enkele node met al zijn relaties
- [ ] `GET /api/v1/graph/edges` — alle edges (filter op cluster, polarity, type)
- [ ] `GET /api/v1/graph/domains` — overzicht van domeinen met node-counts
- [ ] `GET /api/v1/graph/sliders` — alle beleidsinstrumenten
- [ ] Response format: JSON (default) en TOON (`Accept: application/toon`)
- [ ] OpenAPI/Swagger documentatie automatisch gegenereerd
- [ ] Rate limiting per API key

## Technische notities
- Toevoegen aan bestaande FastAPI app
- Graph uit JSON laden bij startup, cachen in geheugen
- Pydantic models voor response types
EOF
)")
echo "  Created: $S4"

S5=$(gh issue create --repo "$REPO" \
  --title "Graph API: causale padanalyse endpoint" \
  --label "story,area: api,priority: medium,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beleidsmedewerker (via LLM-agent)
**Wil ik** kunnen vragen "welke factoren beïnvloeden sportdeelname?"
**Zodat** de agent het causale pad kan traceren en uitleggen

## Acceptatiecriteria
- [ ] `GET /api/v1/graph/paths?from={node_id}&to={node_id}` — alle causale paden tussen twee nodes
- [ ] `GET /api/v1/graph/impact/{node_id}` — upstream/downstream impact analyse
- [ ] Response bevat pad-nodes, edge-gewichten, en mechanisme-beschrijvingen
- [ ] Maximale padlengte configureerbaar (default: 5)
EOF
)")
echo "  Created: $S5"

S6=$(gh issue create --repo "$REPO" \
  --title "Graph API: slider-simulatie endpoint" \
  --label "story,area: api,priority: medium,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beleidsmaker (via LLM-agent)
**Wil ik** kunnen simuleren wat er gebeurt als ik een beleidsinstrument (slider) aanpas
**Zodat** ik de verwachte impact op sportdeelname kan inschatten

## Acceptatiecriteria
- [ ] `POST /api/v1/graph/simulate` — slider-waarden als input, verwachte impact als output
- [ ] Response bevat beïnvloede nodes met richting en sterkte
- [ ] Meerdere sliders tegelijk aanpasbaar
- [ ] Resultaat bevat uitleg van het causale mechanisme
EOF
)")
echo "  Created: $S6"

# ---------------------------------------------------------------------------
# EPIC 3 stories: Ready-made Agent
# ---------------------------------------------------------------------------

S7=$(gh issue create --repo "$REPO" \
  --title "Agent: OpenAPI spec + Copilot Studio declarative agent definitie" \
  --label "story,area: agent,priority: high,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beheerder
**Wil ik** een kant-en-klare agent-definitie leveren aan sportbonden
**Zodat** zij in Copilot Studio met één klik de Sportdeelname-agent kunnen activeren

## Acceptatiecriteria
- [ ] OpenAPI 3.1 spec die de Graph API volledig beschrijft
- [ ] Copilot Studio declarative agent manifest (JSON)
- [ ] Systeem-prompt voor de agent met instructies over het causale model
- [ ] Voorbeeld-conversaties (few-shot examples) in de agent-config
- [ ] Installatie-handleiding (max 5 stappen) voor de sportbond-admin

## Technische notities
- Copilot Studio declarative agents: https://learn.microsoft.com/copilot-studio
- De agent roept de Graph API aan, niet het hele JSON-bestand
- Agent systeem-prompt moet domeinkennis bevatten (wat is een causaal model, hoe werken sliders)
EOF
)")
echo "  Created: $S7"

S8=$(gh issue create --repo "$REPO" \
  --title "Agent: systeem-prompt en conversation design" \
  --label "story,area: agent,priority: high,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** sportbondmedewerker
**Wil ik** in natuurlijke taal vragen kunnen stellen aan de Sportdeelname-agent
**Zodat** ik zonder technische kennis inzicht krijg in het causale model

## Acceptatiecriteria
- [ ] Systeem-prompt die de agent instrueert over:
  - Het KNSB sportdeelnamemodel en de context
  - Hoe causale relaties te interpreteren en uit te leggen
  - Wanneer welk API endpoint aan te roepen
  - Hoe slider-simulaties te presenteren
- [ ] Voorbeeldvragen en -antwoorden:
  - "Welke factoren beïnvloeden recreatieve deelname?"
  - "Wat gebeurt er als we de licentiekosten verlagen?"
  - "Welke psychologische factoren spelen een rol?"
- [ ] Tone of voice: toegankelijk, niet-technisch, Nederlands
- [ ] Fallback-gedrag wanneer een vraag buiten scope valt
EOF
)")
echo "  Created: $S8"

S9=$(gh issue create --repo "$REPO" \
  --title "Agent: BYOK (Bring Your Own Key) authenticatie" \
  --label "story,area: agent,area: api,priority: medium,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** sportbond
**Wil ik** de agent gebruiken binnen mijn eigen M365 Copilot licentie
**Zodat** ik geen extra kosten betaal aan de modelbeheerder voor LLM-tokens

## Acceptatiecriteria
- [ ] Agent draait volledig binnen de Copilot-omgeving van de gebruiker (eigen tokens)
- [ ] Graph API vereist alleen een lichtgewicht API-key (geen LLM-kosten)
- [ ] API-key uitgifte per sportbond via admin-panel of self-service
- [ ] Rate limiting per API-key (fair use)
- [ ] Geen gebruikersdata opgeslagen door de Graph API
EOF
)")
echo "  Created: $S9"

# ---------------------------------------------------------------------------
# EPIC 4 stories: Hosting & Infra
# ---------------------------------------------------------------------------

S10=$(gh issue create --repo "$REPO" \
  --title "Infra: Graph API hosten (Azure / Railway / Fly.io)" \
  --label "story,area: infra,priority: high,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** beheerder
**Wil ik** de Graph API publiek beschikbaar hosten
**Zodat** sportbonden hun agents erop kunnen aansluiten

## Acceptatiecriteria
- [ ] API gehost op publiek bereikbare URL met HTTPS
- [ ] Automatische deployment bij push naar main
- [ ] Health check endpoint (`/health`)
- [ ] Uptime monitoring
- [ ] Kosten < €10/maand bij normaal gebruik
- [ ] Environment variabelen voor configuratie (API keys, rate limits)
EOF
)")
echo "  Created: $S10"

S11=$(gh issue create --repo "$REPO" \
  --title "Infra: SharePoint distributie van DOCX export" \
  --label "story,area: infra,priority: low,fase: 2" \
  --body "$(cat <<'EOF'
## User Story
**Als** sportbondmedewerker
**Wil ik** het sportdeelnamemodel als Word-document op onze SharePoint vinden
**Zodat** mijn M365 Copilot het automatisch kan doorzoeken

## Acceptatiecriteria
- [ ] Documentatie hoe een sportbond-admin het .docx bestand op SharePoint plaatst
- [ ] Optioneel: automatische upload via Microsoft Graph API bij model-update
- [ ] Instructie voor Copilot Notebook setup met SharePoint-referentie
EOF
)")
echo "  Created: $S11"

# ---------------------------------------------------------------------------
# Nu de Epics aanmaken met verwijzingen naar stories
# ---------------------------------------------------------------------------

echo ""
echo "=== Epics aanmaken ==="

gh issue create --repo "$REPO" \
  --title "EPIC: TOON & DOCX Export — token-efficiënte distributie van het model" \
  --label "epic,area: export,fase: 2" \
  --body "$(cat <<EOF
## Doel
Het sportdeelnamemodel beschikbaar maken in formaten die optimaal zijn voor LLM-consumptie (TOON) en SharePoint-indexing (DOCX).

## Waarom
- JSON kost ~40K tokens per sessie → TOON bespaart 40-50%
- Gebruikers betalen eigen tokens → elke besparing telt
- SharePoint/Copilot indexeert .docx beter dan .json

## Stories
- [ ] $S1
- [ ] $S2
- [ ] $S3

## Definition of Done
- Graph is beschikbaar in JSON, TOON, en DOCX formaat
- Bij elke graph-update worden afgeleide formaten automatisch geregenereerd
- Tokenreductie is gemeten en gedocumenteerd
EOF
)"
echo "  Created Epic 1: TOON & DOCX Export"

gh issue create --repo "$REPO" \
  --title "EPIC: Graph API — het causale model als service" \
  --label "epic,area: api,fase: 2" \
  --body "$(cat <<EOF
## Doel
Een lichtgewicht REST API die het sportdeelnamemodel ontsluiten voor externe agents en tools.

## Waarom
- 170KB JSON past niet efficiënt in elke LLM-context
- Gerichte queries (1 node, 1 pad) zijn veel token-efficiënter
- Centrale API = één bron van waarheid, altijd up-to-date
- Gebruikers hoeven geen bestanden te downloaden of updaten

## Stories
- [ ] $S4
- [ ] $S5
- [ ] $S6

## Definition of Done
- API is live, gedocumenteerd (OpenAPI), en beveiligd met API keys
- Endpoints voor nodes, edges, paden, en slider-simulatie
- Response in JSON en TOON formaat
EOF
)"
echo "  Created Epic 2: Graph API"

gh issue create --repo "$REPO" \
  --title "EPIC: Ready-made Copilot Agent — sportdeelname-assistent voor bonden" \
  --label "epic,area: agent,fase: 2" \
  --body "$(cat <<EOF
## Doel
Een kant-en-klare AI-agent die sportbonden in hun eigen M365 Copilot-omgeving kunnen installeren om het sportdeelnamemodel te bevragen.

## Waarom
- Sportbondmedewerkers zijn geen techneuten
- Ze hebben al M365 Copilot (eigen tokens)
- Een ready-made agent verlaagt de drempel tot nul
- BYOK: geen extra kosten voor de beheerder

## Stories
- [ ] $S7
- [ ] $S8
- [ ] $S9

## Definition of Done
- Agent-definitie beschikbaar als importeerbaar pakket voor Copilot Studio
- Installatie-handleiding van max 5 stappen
- Agent kan vragen beantwoorden over het causale model in het Nederlands
- Alle LLM-kosten draaien op de licentie van de sportbond (BYOK)
EOF
)"
echo "  Created Epic 3: Ready-made Copilot Agent"

gh issue create --repo "$REPO" \
  --title "EPIC: Hosting & Distributie-infrastructuur" \
  --label "epic,area: infra,fase: 2" \
  --body "$(cat <<EOF
## Doel
De Graph API en exports hosten en distribueren zodat sportbonden er eenvoudig toegang toe hebben.

## Waarom
- API moet publiek bereikbaar zijn voor Copilot agents
- Automatische deployment houdt alles in sync
- SharePoint-distributie voor organisaties die geen API-integratie willen

## Stories
- [ ] $S10
- [ ] $S11

## Definition of Done
- API live op publieke URL met HTTPS
- CI/CD pipeline voor automatische deployment
- Documentatie voor SharePoint-distributie
EOF
)"
echo "  Created Epic 4: Hosting & Distributie"

echo ""
echo "=== Klaar! ==="
echo "Alle labels, stories en epics zijn aangemaakt."
echo "Bekijk ze op: https://github.com/$REPO/issues"
