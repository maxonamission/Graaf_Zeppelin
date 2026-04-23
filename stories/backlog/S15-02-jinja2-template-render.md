# S15-02: Jinja2-render faalt in 5 pagina-tests

**Epic:** EPIC-15 Testsuite-rehabilitatie
**Status:** 🔲 Backlog
**Prioriteit:** GEMIDDELD
**Bron:** Gevonden tijdens S14-01-validatie (2026-04-23)

## Probleem

Na S15-01 (async-plugin hersteld) blijft een **kleine, inhoudelijke** groep
failures staan: 5 tests die een HTML-pagina renderen crashen op Jinja2 met

```
TypeError: unhashable type: 'dict'
  at .venv/lib/python3.11/site-packages/jinja2/utils.py:515
```

Jinja2 probeert daar een waarde als cache-key te gebruiken via `hash(...)`;
een dict kan niet gehashed worden. Concreet betekent dat: ergens in het
template of in de context wordt een dict op een plek gebruikt waar Jinja2
een hashable waarde verwacht (bv. als argument van een filter of macro dat
iets memoized, of binnen een constructie als een set/dict-literal).

## Getroffen tests

| Test | Doel |
|---|---|
| `tests/test_sprint4.py::test_graph_viewer_page_loads` | GET op graph-viewer pagina |
| `tests/test_sprint4.py::test_license_page_shows_tier_comparison` | GET op licentiepagina |
| `tests/test_sprint4.py::test_dashboard_shows_onboarding` | GET op dashboard |
| `tests/test_wizard_and_byok.py::test_dashboard_page_loads` | GET op dashboard |
| `tests/test_wizard_and_byok.py::test_wizard_page_loads` | GET op wizard |

Allemaal zijn het sync tests met `TestClient` die een pagina opvragen; de
API-laag werkt — het faalt pas in `render_template`.

**Belangrijke observatie:** deze tests renderen echte gebruikerspagina's.
Een render-failure hier betekent dat de **pagina's zelf** mogelijk in
productie ook crashen onder bepaalde omstandigheden, niet alleen in de test.
Dat verdient snelle opheldering — niet omdat het veel tests zijn, maar
omdat het gebruikers kan raken.

## Doel

Identificeren welk template of welke template-context de dict-in-hash-
positie veroorzaakt; repareren; de 5 tests op groen; verifiëren dat de
betrokken pagina's in de dev-server zonder fout laden.

## Acceptatiecriteria

- [ ] Root cause geïdentificeerd: welk template, welke regel, welke variabele
      wordt als hash-key gebruikt terwijl het een dict is
- [ ] Fix toegepast op het template **of** op de context-voorbereiding in de
      route — afhankelijk van wat het juiste niveau is
- [ ] 5 genoemde tests groen
- [ ] Handmatige sanity-check in dev-browser: dashboard, graph-viewer,
      licentiepagina, wizard laden zonder 500
- [ ] Regressietest: minimaal één test die de specifieke context-vorm
      expliciet dekt (bv. "graph-summary met lege domain-dict rendert niet
      crashen")

## Aanpak

1. Run één falende test met `--tb=long -s`; vang de volledige Jinja2-traceback
   (welke template, welke regel, welke filter/macro)
2. Lokaliseer in `app/templates/` het template + regelnummer
3. Inspecteer de context die de route meegeeft: is er een veld dat een dict
   is waar het string/tuple/int zou moeten zijn? Of wordt `{% set %}`
   gebruikt met dict-waarden in een context die een hash nodig heeft?
4. Fix op laagste niveau: als het een eenmalige template-bug is, repareer
   template; als het een context-bug is, repareer de route
5. Draai de 5 tests + handmatig de pagina's
6. Korte regressietest als vangnet

## Afhankelijkheden

S15-01 moet eerst — zonder async-plugin komen deze pagina's niet eens uit de
collection-fase.

## Geschat

2–4 uur, afhankelijk van hoe ver de dict-in-hash-positie is weggestopt.
Grote kans dat het één template-regel is die over alle 5 pagina's heen
via een gedeeld `base.html` of partial doorwerkt.

## Risico's

- De root cause ligt in een shared partial (bv. navigatie, footer). Fix
  in één klap, maar test-impact breder dan de 5 failures. Mitigeer met
  brede handmatige check na de fix.
- Als het context-data is die uit de DB komt, kan er ook productie-data
  onverwachte vormen hebben. Bij twijfel: een defensieve normalisatie in
  de route-laag toevoegen, niet in het template.
