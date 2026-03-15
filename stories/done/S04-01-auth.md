# S04-01: Auth — JWT, wachtwoordhashing, login/registratie

**Epic:** EPIC-04 Authenticatie & licenties
**Status:** ✅ Done
**Module:** `app/core/auth.py` (93 regels)

## Beschrijving

Authenticatie met JWT tokens en wachtwoordhashing (stdlib-only).

## Wat is gebouwd

- JWT (HS256) token generatie en validatie
- Bcrypt wachtwoordhashing (cost factor 12)
- Login en registratie endpoints
- Cookie-based sessies
