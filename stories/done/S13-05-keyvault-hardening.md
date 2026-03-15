# S13-05 — KeyVault en cryptografie hardening

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** ✅ Done

## Doel

De twee resterende cryptografische bevindingen uit de audit (G6, G7) oplossen: de key-derivatie in de KeyVault versterken en SSL op de database-verbinding afdwingen in productie.

## Wat we al hebben

- Fernet-encryptie voor opgeslagen API-keys (via KeyVault)
- SECRET_KEY validatie bij opstart (lengte, complexiteit)
- bcrypt voor wachtwoordhashing

## Wat er mist

- **G6**: De encryptiesleutel voor de KeyVault wordt afgeleid via een enkele SHA-256 hash van de SECRET_KEY. Dit biedt geen *key stretching* — als de SECRET_KEY ooit lekt, zijn alle opgeslagen API-keys direct te ontsleutelen.
- **G7**: De database-verbinding dwingt geen SSL af. In een productieomgeving met gescheiden servers is het netwerkverkeer tussen app en database onversleuteld.

## Acceptatiecriteria

- [x] KeyVault key-derivatie vervangen door PBKDF2 (480.000 iteraties, OWASP 2023)
- [x] Migratiestrategie: MultiFernet (PBKDF2 primary, SHA-256 legacy fallback) — backward compatible zonder her-encryptie
- [x] Database-verbinding valideert `sslmode` in productie (waarschuwing als ontbreekt)
- [x] Alle 214 bestaande tests slagen
- [x] Wijzigingen gedocumenteerd in `.env.example`

## Afhankelijkheden

- Geen
