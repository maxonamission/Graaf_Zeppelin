# Server & Hosting — Afweging en Advies

> **Doelgroep**: Graaf Zeppelin v2 (FastAPI + PostgreSQL)
> **Verwacht gebruik**: 1–100 gebruikers, lichte belasting, LLM-calls naar externe API's
> **Vereisten**: Docker-ready, `.env` configuratie, HTTPS, EU-hosting (AVG)

---

## 1. De drie opties op een rij

### Optie A: VPS (Virtual Private Server)

**Wat is het?** Een virtuele Linux-machine die je huurt. Je installeert zelf alles.

| Aspect | Details |
|--------|---------|
| **Providers** | Hetzner (Falkenstein/Neurenberg), TransIP (NL), DigitalOcean (AMS), Vultr |
| **Kosten** | €4–15/mnd voor 2 vCPU, 4 GB RAM, 40 GB SSD |
| **Geschikt voor** | Kleine tot middelgrote deployments, volledige controle |
| **Voordeel** | Goedkoop, eenvoudig, alles op één machine |
| **Nadeel** | Zelf beheren: updates, backups, SSL, monitoring |
| **Leercurve** | Laag-gemiddeld (basis Linux + Docker) |

**Aanbevolen provider**: **Hetzner Cloud** — beste prijs/kwaliteit in EU, datacenters in Duitsland.
- CPX11 (2 vCPU, 2 GB): €4,85/mnd — voldoende voor start
- CPX21 (3 vCPU, 4 GB): €8,49/mnd — comfortabel voor productie

### Optie B: Managed Platform (PaaS)

**Wat is het?** Een platform dat de server voor je beheert. Jij pusht code, zij draaien het.

| Aspect | Details |
|--------|---------|
| **Providers** | Railway, Render, Fly.io, Google Cloud Run |
| **Kosten** | €5–25/mnd (app + database apart) |
| **Geschikt voor** | Snelle start, geen serverbeheer |
| **Voordeel** | Geen Linux-kennis nodig, auto-deploy vanuit Git |
| **Nadeel** | Minder controle, kan duurder worden bij groei, vendor lock-in |
| **Leercurve** | Laag |

**Aanbevolen provider**: **Railway** — simpelste DX, PostgreSQL inbegrepen, EU-regio beschikbaar.
- Starter: ~€5/mnd (app + database)
- Pro: ~€10–20/mnd met meer resources

### Optie C: Eigen server / on-premise

| Aspect | Details |
|--------|---------|
| **Geschikt voor** | Organisaties met eigen IT-infra of strenge datavereisten |
| **Voordeel** | Volledige controle, data blijft intern |
| **Nadeel** | Veel beheerwerk, hardware-investering |
| **Leercurve** | Hoog |

> **Niet aanbevolen** tenzij de organisatie dit specifiek vereist.

---

## 2. Mijn advies

### Voor jouw situatie: **Optie A (VPS bij Hetzner)** ⟵ aanbevolen

Waarom:
1. **Je hebt Docker al** — `Dockerfile` en `docker-compose.yml` zijn klaar
2. **Kosten**: €5–9/mnd alles-in (server + database + app)
3. **EU-hosting**: Hetzner datacenters in Duitsland (AVG-compliant)
4. **Leerzaam**: je leert basis-serverbeheer wat nuttig is voor de toekomst
5. **Schaalbaar**: later upgraden is één knop in het dashboard
6. **Geen vendor lock-in**: standaard Linux, verhuizen kan altijd

### Wanneer wél Railway (Optie B)?
- Als je **echt geen** Linux-terminal wilt aanraken
- Als je **direct** live wilt zonder setup-tijd
- Als de extra €5–10/mnd niet uitmaakt

---

## 3. Wat je nodig hebt (voor Optie A: Hetzner VPS)

### Vóór de installatie
- [ ] Hetzner Cloud account (gratis aanmaken)
- [ ] Een domeinnaam (optioneel maar aanbevolen, ~€10/jaar)
- [ ] SSH key pair (wordt gegenereerd tijdens setup)
- [ ] Je `.env` waardes: `SECRET_KEY`, `DATABASE_URL`, eventueel LLM API keys

### Wat er op de server komt
```
┌─────────────────────────────────────┐
│  Hetzner VPS (Ubuntu 24.04)         │
│                                     │
│  ┌──────────────┐  ┌─────────────┐  │
│  │  Docker       │  │  Caddy      │  │
│  │  ┌──────────┐ │  │  (reverse   │  │
│  │  │ Graaf    │ │  │   proxy +   │  │
│  │  │ Zeppelin │ │◄─┤   HTTPS)    │◄─── internet
│  │  │ :8000    │ │  │  :443       │  │
│  │  └──────────┘ │  └─────────────┘  │
│  │  ┌──────────┐ │                   │
│  │  │PostgreSQL│ │                   │
│  │  │ :5432    │ │                   │
│  │  └──────────┘ │                   │
│  └──────────────┘                    │
└─────────────────────────────────────┘
```

### Geschatte maandkosten

| Component | Kosten |
|-----------|--------|
| Hetzner VPS (CPX11) | €4,85 |
| Domeinnaam (optioneel) | ~€1 |
| **Totaal** | **~€6/mnd** |

> PostgreSQL, HTTPS (Let's Encrypt), en backups draaien allemaal op dezelfde VPS.
> LLM-kosten (OpenAI/Anthropic) komen daar apart bij, afhankelijk van gebruik.

---

## 4. Vergelijking samengevat

| Criterium | VPS (Hetzner) | PaaS (Railway) | On-premise |
|-----------|:---:|:---:|:---:|
| Kosten/mnd | €5–9 | €10–25 | €€€ |
| Setup-tijd | ~1 uur | ~15 min | Dagen |
| Linux-kennis nodig | Basis | Nee | Veel |
| Volledige controle | Ja | Beperkt | Ja |
| Auto-deploy vanuit Git | Nee* | Ja | Nee |
| EU-hosting (AVG) | Ja | Mogelijk | Ja |
| Schalen | Handmatig | Automatisch | Handmatig |
| Downtime bij deploy | ~10 sec | 0 | Variabel |

*\* Kan je instellen met GitHub Actions, maar dat is extra configuratie.*

---

## 5. Volgende stap

Maak een keuze en laat het me weten. Ik schrijf dan een **stap-voor-stap installatiehandleiding** specifiek voor die optie, inclusief:

- Account aanmaken en server bestellen
- SSH-verbinding opzetten
- Docker + PostgreSQL installeren
- `docker-compose.yml` aanpassen voor productie
- HTTPS instellen (automatisch via Caddy of Certbot)
- Domeinnaam koppelen
- Eerste deploy uitvoeren
- Backup-strategie
- Monitoring basis

Welke optie spreekt je aan?
