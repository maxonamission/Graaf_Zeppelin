# S11-02 — API- en frontend-bescherming (input, transport, XSS, headers)

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: KRITIEK/HOOG — vóór productie
**Geschatte omvang**: L
**Status:** 🔶 Deels geïmplementeerd

## Doel

API-endpoints en frontend beschermen tegen injection, CSRF, XSS, en transport-aanvallen.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| K3 | API-keys in plaintext request bodies | KRITIEK | CWE-319 |
| H5 | Ontbrekende CSRF-bescherming | HOOG | CWE-352 |
| H6 | Geen input-lengtevalidatie op LLM-prompts | HOOG | CWE-20 |
| F1 | DOM-XSS via innerHTML in login/register/graph | HOOG | CWE-79 |
| F3 | Ontbrekende Content Security Policy | GEMIDDELD | CWE-693 |
| F4 | Onvolledige escapeAttr() in reasoning.html | GEMIDDELD | CWE-79 |
| L1 | Ontbrekende HTTP-beveiligingsheaders | LAAG | CWE-693 |
| L4 | Geen SRI op CDN-scripts (htmx, D3) | LAAG | CWE-829 |

## Acceptatiecriteria

### Backend
- [ ] Reasoning/wizard endpoints accepteren alleen `stored_key_id` (int), niet raw API keys ❌ raw api_key nog geaccepteerd
- [x] Bestaande BYOK-flow werkt via opgeslagen keys
- [x] Input-validatie op alle user-facing strings:
  - `query`/`question`: max 2.000 tekens
  - `factor_id`: max 100 tekens, alfanumeriek + underscore
  - `model_id`: max 100 tekens, alfanumeriek + underscore/hyphen
- [x] CSRF-token op alle state-changing endpoints (POST, PUT, DELETE)
- [x] Security headers middleware:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security: max-age=31536000`
- [ ] Geen raw exception details in API responses ⚠️ sommige endpoints tonen nog str(e)

### Frontend (XSS/CSP)
- [x] `login.html`: `data.detail` via `textContent` i.p.v. `innerHTML`
- [x] `register.html`: idem
- [ ] `graph_viewer.html`: domein-namen en factor-ID's in onclick via `data-*` attributen + event delegation i.p.v. string-interpolatie ❌ nog inline onclick
- [ ] `reasoning.html`: `escapeAttr()` vervangen door `JSON.stringify()` voor attribuutwaarden ❌ nog escapeAttr()
- [ ] Alle `innerHTML` paden consistent via `escapeHtml()` of `textContent` ⚠️ deels
- [x] Content Security Policy header:
  ```
  Content-Security-Policy: default-src 'self'; script-src 'self' https://unpkg.com https://d3js.org; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'
  ```
- [ ] SRI-hashes op externe scripts (htmx, D3): ❌ niet geïmplementeerd
  ```html
  <script src="https://d3js.org/d3.v7.min.js"
          integrity="sha384-..." crossorigin="anonymous"></script>
  ```

## Technische notities

- CSRF: `fastapi-csrf-protect` of custom double-submit cookie
- Headers: Starlette `BaseHTTPMiddleware`
- CSP: D3.js en htmx CDN's toestaan als `script-src`
- Input: Pydantic `Field(max_length=...)` op alle string-velden
- XSS: Vervang dynamische `onclick="fn('${var}')"` door `data-id="${escapeHtml(var)}"` + `addEventListener`
- SRI: Genereer hashes met `openssl dgst -sha384 -binary < d3.v7.min.js | openssl base64 -A`

## Herhaalbaar

Bij elk nieuw API-endpoint of template-wijziging, checklist doorlopen:
1. Input-validatie aanwezig? (max lengte, type, format)
2. Authenticatie vereist?
3. CSRF-bescherming op state-changing routes?
4. Geen innerHTML met user-data zonder escaping?
5. Externe scripts met SRI?
