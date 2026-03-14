# S02-01: Slider Engine — 3 curvemodellen, multi-slider simulatie

**Epic:** EPIC-02 Interventie-simulatie met sliders
**Status:** ✅ Done
**Module:** `app/core/slider_engine.py` (209 regels)

## Beschrijving

Engine die beleidssliders vertaalt naar effecten op het causale model via
drie wiskundige curvemodellen.

## Wat is gebouwd

- Dampening threshold — drempelwaarde, daaronder neutraal, daarboven exponentieel
- Inverted-U — optimum, zowel te weinig als te veel is negatief
- Linear — proportioneel effect
- Multi-slider combinatie (multiplicatief, niet additief)
- 5 gevoeligheidsniveaus per edge

## Tests

12 tests in `tests/test_slider_engine.py` — alle slagen.
