# Dependency Lifecycle Management — Handleiding en Noodzaak-inschatting

> **Versie**: 1.0
> **Datum**: 15 maart 2026
> **Context**: Story S13-04 (EPIC-13 Beveiligingsvervolg)

---

## 1. Noodzaak-inschatting

### Is Dependabot (of vergelijkbaar) nodig voor Graaf Zeppelin?

**Korte antwoord**: Ja, en het is eenvoudig in te richten. De investering is minimaal (< 30 minuten), het rendement is hoog.

### Huidige situatie

| Aspect | Status |
|--------|--------|
| **pip-audit in CI** | ✅ Draait per kwartaal (S11-05) |
| **bandit + semgrep** | ✅ Draait bij elke push |
| **Automatische CVE-notificaties** | ❌ Niet ingeschakeld |
| **Versie-pinning** | ⚠️ Minimumversies (`>=`), geen lock-file |
| **Patch-SLA** | ❌ Niet gedefinieerd |

### Waarom wel inschakelen

| Argument | Toelichting |
|----------|------------|
| **Zero-day reactietijd** | Een kritieke CVE in `httpx`, `cryptography`, of `fastapi` kan binnen uren actief worden misbruikt. Dependabot meldt dit automatisch, pip-audit pas bij de volgende kwartaalscan. |
| **Geen extra kosten** | GitHub Dependabot is gratis voor alle repositories (publiek én privaat). |
| **Minimale overhead** | Dependabot maakt automatisch een PR met de versie-update. Je hoeft alleen te reviewen en mergen. |
| **Compliance** | Aantoonbare dependency-monitoring is een "passende technische maatregel" in de context van AVG art. 32. |
| **Supply chain risico** | Graaf Zeppelin heeft 15 directe dependencies. Elk daarvan heeft transitive dependencies. Het handmatig bijhouden van CVE's voor deze hele keten is onpraktisch. |

### Waarom het niet urgent is

| Argument | Toelichting |
|----------|------------|
| **Klein dependency-oppervlak** | 15 directe dependencies, allemaal van gevestigde maintainers (FastAPI, SQLAlchemy, cryptography). |
| **pip-audit draait al** | Kwetsbaarheidsdetectie is er al, alleen niet realtime. |
| **Beperkt productiegebruik** | Zolang de applicatie niet breed in productie draait, is het risico van een ongepatcht CVE beperkt. |

### Aanbeveling

| Actie | Wanneer |
|-------|---------|
| **Dependabot inschakelen** | Nu — kost < 30 minuten, geen reden om te wachten |
| **Lock-file toevoegen** | Bij eerste productie-deployment |
| **Patch-SLA definiëren** | Nu (zie sectie 4) |

---

## 2. Dependabot configuratie

### Stap 1: Maak het configuratiebestand aan

Maak het bestand `.github/dependabot.yml` aan in de repository:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Europe/Amsterdam"
    # Beperk het aantal open PRs om review-overhead te beperken
    open-pull-requests-limit: 5
    # Groepeer minor/patch updates om PR-ruis te verminderen
    groups:
      minor-and-patch:
        update-types:
          - "minor"
          - "patch"
    # Security updates worden altijd apart gemeld (niet gegroepeerd)
    # en hebben geen last van de open-pull-requests-limit
```

### Stap 2: Schakel Dependabot security alerts in

1. Ga naar de repository op GitHub
2. **Settings** → **Code security and analysis**
3. Schakel in:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates

### Stap 3 (optioneel): GitHub Actions notificatie

Dependabot stuurt standaard een notificatie via GitHub. Voor een extra melding in Slack of e-mail, configureer een GitHub Actions workflow:

```yaml
# .github/workflows/dependabot-notify.yml
name: Dependabot alert notify
on:
  dependabot_alert:
    types: [created]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send notification
        # Configureer naar eigen voorkeur (Slack webhook, e-mail, etc.)
        run: echo "New Dependabot alert — check GitHub"
```

---

## 3. Lock-file strategie

### Huidig: minimumversies (`>=`)

```
# requirements.txt (huidig)
fastapi>=0.104.0
cryptography>=41.0.0
```

**Voordeel**: Flexibel, pakt automatisch compatibele updates mee.
**Nadeel**: Builds zijn niet 100% reproduceerbaar. Twee installaties op verschillende momenten kunnen andere versies opleveren.

### Aanbevolen: dubbel bestand

```
# requirements.txt — bron (menselijk beheerd)
fastapi>=0.104.0
cryptography>=41.0.0

# requirements-lock.txt — gegenereerd (pip freeze)
fastapi==0.115.8
cryptography==44.0.1
...
```

**Gebruik**:
- Development: `pip install -r requirements.txt` (flexibel)
- Productie / CI: `pip install -r requirements-lock.txt` (exact)
- Regenereer lock-file: `pip freeze > requirements-lock.txt`

**Wanneer**: Bij eerste productie-deployment. In development-fase is de flexibiliteit van minimumversies handiger.

---

## 4. Patch-SLA

| Ernst (CVSS) | Termijn | Voorbeeld |
|--------------|---------|-----------|
| **Kritiek** (9.0–10.0) | **48 uur** | Remote code execution in httpx, cryptography |
| **Hoog** (7.0–8.9) | **1 week** | Authentication bypass in FastAPI |
| **Gemiddeld** (4.0–6.9) | **Volgende sprint** | Information disclosure in SQLAlchemy |
| **Laag** (0.1–3.9) | **Volgende kwartaal-update** | Minor timing side-channel |

### Proces bij een CVE-melding

1. **Dependabot PR verschijnt** of pip-audit meldt een kwetsbaarheid
2. **Security Champion triageert**: is de kwetsbaarheid relevant voor ons gebruik?
   - Niet relevant → sluit PR met toelichting
   - Relevant → classificeer op basis van CVSS-score
3. **Developer past toe**: merge PR, draai tests, deploy
4. **Documenteer**: noteer CVE-nummer en actie in het security-log

---

## 5. Kwartaalschema voor bewuste updates

Niet alle updates zijn security-gerelateerd. Het is gezond om dependencies periodiek te updaten, ook zonder CVE-aanleiding:

| Kwartaal | Actie |
|----------|-------|
| **Q1** | Volledige `pip install --upgrade` + `pip freeze` → lock-file regeneratie |
| **Q2** | Controleer of er major version updates beschikbaar zijn (breaking changes?) |
| **Q3** | Volledige update + lock-file regeneratie |
| **Q4** | Jaarlijkse review: zijn er dependencies die niet meer onderhouden worden? Alternatieven zoeken. |

---

## 6. Graaf Zeppelin dependency-overzicht

Huidige directe dependencies (15 stuks) en hun risicoprofiel:

| Dependency | Versie (min) | Risicoprofiel | Toelichting |
|-----------|-------------|---------------|------------|
| `fastapi` | ≥0.104.0 | Gemiddeld | Web framework, direct blootgesteld aan internet |
| `uvicorn` | ≥0.24.0 | Gemiddeld | ASGI-server, verwerkt alle HTTP-traffic |
| `sqlalchemy` | ≥2.0.0 | Laag | ORM, niet direct blootgesteld |
| `alembic` | ≥1.13.0 | Laag | Migratietool, draait alleen bij deployment |
| `networkx` | ≥3.2.0 | Laag | Grafenbibliotheek, geen netwerk-interactie |
| `jinja2` | ≥3.1.0 | Gemiddeld | Template engine, XSS-risico bij fout gebruik |
| `python-multipart` | ≥0.0.6 | Gemiddeld | Form parsing, historisch kwetsbaar geweest |
| `httpx` | ≥0.25.0 | Hoog | HTTP-client richting LLM-providers, verwerkt API-keys |
| `pydantic` | ≥2.5.0 | Laag | Validatiebibliotheek |
| `pydantic-settings` | ≥2.1.0 | Laag | Configuratie-parsing |
| `aiosqlite` | ≥0.19.0 | Laag | SQLite async driver (alleen development) |
| `asyncpg` | ≥0.29.0 | Gemiddeld | PostgreSQL driver (productie), verwerkt DB-credentials |
| `cryptography` | ≥41.0.0 | **Hoog** | Kernbibliotheek voor KeyVault, historisch frequente CVE's |
| `bcrypt` | ≥4.1.0 | Laag | Wachtwoordhashing, stabiele API |
| `slowapi` | ≥0.1.9 | Laag | Rate limiting middleware |

**Prioriteit voor monitoring**: `cryptography`, `httpx`, `fastapi`, `uvicorn`, `asyncpg`

---

## 7. Relatie met andere documenten

- **Incident response plan** (`docs/incident-response-plan.md`): Sectie 4.4 beschrijft het stappenplan bij een CVE-melding
- **Security review proces** (`docs/security-review-proces.md`): Dependency-checks zijn onderdeel van de PR-checklist en kwartaalplanning
- **Beveiligingsaudit** (`docs/beveiligingsaudit-v2.md`): Bevinding G7 (dependency monitoring) is de aanleiding voor dit document
