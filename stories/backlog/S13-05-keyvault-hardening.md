# S13-05 — KeyVault en cryptografie hardening

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** 🔲 Backlog

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

- [ ] KeyVault key-derivatie vervangen door PBKDF2 (≥100.000 iteraties) of aparte `ENCRYPTION_MASTER_KEY` omgevingsvariabele
- [ ] Migratiestrategie voor bestaande versleutelde keys (her-encryptie of backward-compatible)
- [ ] Database-verbinding valideert `sslmode` in productie (waarschuwing of fout als ontbreekt)
- [ ] Bestaande tests slagen
- [ ] Wijzigingen gedocumenteerd in `.env.example`

## Afhankelijkheden

- Geen
