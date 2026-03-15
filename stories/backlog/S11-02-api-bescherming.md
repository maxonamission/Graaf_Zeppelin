# S11-02 — API-bescherming (input, transport, headers)

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: KRITIEK/HOOG — vóór productie
**Geschatte omvang**: M

## Doel

API-endpoints beschermen tegen injection, CSRF, en transport-aanvallen.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| K3 | API-keys in plaintext request bodies | KRITIEK | CWE-319 |
| H5 | Ontbrekende CSRF-bescherming | HOOG | CWE-352 |
| H6 | Geen input-lengtevalidatie op LLM-prompts | HOOG | CWE-20 |
| L1 | Ontbrekende HTTP-beveiligingsheaders | LAAG | CWE-693 |
| L2 | XSS-risico via innerHTML | LAAG | CWE-79 |

## Acceptatiecriteria

- [ ] Reasoning/wizard endpoints accepteren alleen `stored_key_id` (int), niet raw API keys
- [ ] Bestaande BYOK-flow werkt via opgeslagen keys
- [ ] Input-validatie op alle user-facing strings:
  - `query`/`question`: max 2.000 tekens
  - `factor_id`: max 100 tekens, alfanumeriek + underscore
  - `model_id`: max 100 tekens, alfanumeriek + underscore/hyphen
- [ ] CSRF-token op alle state-changing endpoints (POST, PUT, DELETE)
- [ ] Security headers middleware:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security: max-age=31536000`
  - `Content-Security-Policy: default-src 'self'; script-src 'self' d3js.org; style-src 'self' 'unsafe-inline'`
- [ ] Alle `innerHTML` paden in templates gaan via `escapeHtml()`
- [ ] Geen raw exception details in API responses

## Technische notities

- CSRF: `fastapi-csrf-protect` of custom double-submit cookie
- Headers: Starlette `BaseHTTPMiddleware`
- CSP: D3.js CDN toestaan als `script-src`
- Input: Pydantic `Field(max_length=...)` op alle string-velden

## Herhaalbaar

Bij elk nieuw API-endpoint: checklist doorlopen:
1. Input-validatie aanwezig?
2. Authenticatie vereist?
3. Rate limiting?
4. CSRF-bescherming op state-changing routes?
