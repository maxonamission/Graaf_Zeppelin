# S11-01 — Authenticatie hardening

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: KRITIEK — vóór productie
**Geschatte omvang**: M
**Status:** 🔶 Deels geïmplementeerd

## Doel

Alle authenticatie- en sessiebeheer-kwetsbaarheden oplossen conform OWASP ASVS v4.0 en NIST SP 800-63B.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| K1 | Zwakke wachtwoordhashing (HMAC-SHA256) | KRITIEK | CWE-916 |
| K2 | Hardcoded secret key in broncode | KRITIEK | CWE-798 |
| K4 | Geen rate limiting op login/registratie | KRITIEK | CWE-307 |
| H1 | Geen wachtwoordbeleid (min. lengte/complexiteit) | HOOG | CWE-521 |
| H2 | Ontbrekende secure cookie-flags | HOOG | CWE-614 |
| G1 | Token 24 uur geldig, geen refresh-tokens | GEMIDDELD | CWE-613 |
| G2 | JWT-algoritme niet gevalideerd bij decode | GEMIDDELD | CWE-347 |
| L3 | Account-enumeratie via registratiefoutmelding | LAAG | CWE-204 |

## Acceptatiecriteria

- [x] Wachtwoorden gehasht met bcrypt (cost factor ≥ 12) of argon2id
- [ ] Bestaande wachtwoorden automatisch ge-rehashed bij eerstvolgende login
- [ ] `SECRET_KEY` heeft geen default — app weigert te starten zonder env var ⚠️ default bestaat nog, alleen warning
- [x] `.env` staat in `.gitignore`
- [ ] Rate limiting: max 5 login-pogingen/minuut, max 3 registraties/uur per IP ❌ slowapi geïmporteerd maar incorrect gebruikt
- [x] Wachtwoordbeleid: minimaal 12 tekens, mix van hoofdletters/kleine letters/cijfers
- [ ] Cookie-flags: `HttpOnly=true`, `Secure=true`, `SameSite=lax` ⚠️ Secure=false
- [ ] Token-levensduur teruggebracht naar 30 minuten + refresh-token (7 dagen) ❌ nog 24 uur
- [x] JWT-decode valideert `alg=HS256` header
- [x] Registratiefoutmelding is generiek ("Registratie kon niet worden voltooid")
- [ ] Alle bestaande auth-tests blijven slagen ❌ test_hash_contains_salt faalt (verwacht HMAC-formaat)

## Technische notities

- Dependency toevoegen: `passlib[bcrypt]` of `argon2-cffi`
- Rate limiting: `slowapi` (wraps `limits`) of custom middleware
- Refresh-tokens: apart model in database (niet stateless JWT)
- Migratiescenario: bestaande HMAC-hashes detecteren en bij login vervangen door bcrypt

## Herhaalbaar

Bij elke wijziging aan `auth.py`, `deps.py` of `config.py`: hercontrole op deze criteria.
