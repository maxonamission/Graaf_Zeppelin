# Installatiehandleiding — Hetzner Cloud VPS

> **Doel**: Graaf Zeppelin draaien op een Hetzner VPS met PostgreSQL, HTTPS, en automatische backups.
> **Tijdsinschatting**: ±45 minuten als je de stappen volgt.
> **Vereiste voorkennis**: geen (alles wordt uitgelegd).

---

## Inhoudsopgave

1. [Hetzner account aanmaken](#1-hetzner-account-aanmaken)
2. [Server bestellen](#2-server-bestellen)
3. [Verbinden via SSH](#3-verbinden-via-ssh)
4. [Server voorbereiden](#4-server-voorbereiden)
5. [Graaf Zeppelin deployen](#5-graaf-zeppelin-deployen)
6. [Domeinnaam koppelen (optioneel)](#6-domeinnaam-koppelen-optioneel)
7. [HTTPS instellen](#7-https-instellen)
8. [Backups instellen](#8-backups-instellen)
9. [Updates deployen](#9-updates-deployen)
10. [Problemen oplossen](#10-problemen-oplossen)

---

## 1. Hetzner account aanmaken

1. Ga naar https://www.hetzner.com/cloud/
2. Klik **"Register"** (rechtsboven)
3. Vul je gegevens in (e-mail, naam, adres)
4. Bevestig je e-mail
5. Voeg een betaalmethode toe (creditcard of PayPal)

> **Tip**: Hetzner factureert per uur. Als je de server na een dag verwijdert, betaal je alleen die dag.

---

## 2. Server bestellen

1. Log in op https://console.hetzner.cloud/
2. Klik **"New project"** → noem het `graaf-zeppelin`
3. Open het project → klik **"Add Server"**

Kies deze instellingen:

| Instelling | Keuze |
|-----------|-------|
| **Location** | Falkenstein (FSN1) of Nuremberg (NBG1) — Duitsland, dicht bij NL |
| **Image** | Ubuntu 24.04 |
| **Type** | Shared vCPU → **CPX11** (2 vCPU, 2 GB RAM, 40 GB) — €4,85/mnd |
| **Networking** | IPv4 aanvinken (nodig voor domeinnaam) |
| **SSH Key** | → zie hieronder |
| **Name** | `graaf-zeppelin` |

### SSH key aanmaken (als je er nog geen hebt)

Op **je eigen computer** (niet op de server), open een terminal:

**Mac/Linux:**
```bash
ssh-keygen -t ed25519 -C "graaf-zeppelin"
```

**Windows (PowerShell):**
```powershell
ssh-keygen -t ed25519 -C "graaf-zeppelin"
```

Druk drie keer Enter (standaard locatie, geen wachtwoord).

Kopieer de **publieke** sleutel:
```bash
# Mac/Linux:
cat ~/.ssh/id_ed25519.pub

# Windows (PowerShell):
Get-Content ~/.ssh/id_ed25519.pub
```

Plak de uitvoer in het SSH Key veld bij Hetzner.

4. Klik **"Create & Buy Now"**
5. Wacht ~30 seconden — je server draait

> **Noteer het IP-adres** dat Hetzner toont (bijv. `168.119.xxx.xxx`). Dit heb je straks nodig.

---

## 3. Verbinden via SSH

Open een terminal op je eigen computer:

```bash
ssh root@JOUW_IP_ADRES
```

Vervang `JOUW_IP_ADRES` door het IP uit stap 2.

Bij de eerste keer vraagt hij of je de fingerprint vertrouwt → typ `yes`.

> **Windows**: Gebruik Windows Terminal (ingebouwd in Windows 11) of download [PuTTY](https://www.putty.org/). Windows Terminal ondersteunt `ssh` direct.

Je bent nu ingelogd op je server. Alles hierna typ je **op de server**.

---

## 4. Server voorbereiden

### 4a. Systeem updaten

```bash
apt update && apt upgrade -y
```

### 4b. Firewall instellen

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Typ `y` bij de bevestiging.

### 4c. Docker installeren

```bash
# Officiële Docker installatie (één commando)
curl -fsSL https://get.docker.com | sh

# Docker Compose plugin zit er al bij. Controleer:
docker compose version
```

Je zou iets moeten zien als `Docker Compose version v2.x.x`.

### 4d. Beveiligingsgebruiker aanmaken (aanbevolen)

```bash
# Maak een gebruiker aan (vervang 'deploy' door een naam naar keuze)
adduser deploy
usermod -aG docker deploy
usermod -aG sudo deploy

# Kopieer je SSH key naar de nieuwe gebruiker
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
```

Vanaf nu kun je inloggen met `ssh deploy@JOUW_IP_ADRES`.

---

## 5. Graaf Zeppelin deployen

### 5a. Code op de server zetten

```bash
# Log in als deploy-gebruiker
su - deploy

# Maak een projectmap
mkdir -p ~/apps && cd ~/apps

# Clone de repository
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin
```

> **Geen Git?** Je kunt ook een ZIP uploaden:
> ```bash
> # Op je eigen computer:
> scp -r ./Graaf_Zeppelin deploy@JOUW_IP_ADRES:~/apps/
> ```

### 5b. Productie docker-compose aanmaken

Maak een productie-configuratie aan:

```bash
cat > docker-compose.prod.yml << 'YAML'
services:
  web:
    build: .
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql+asyncpg://graaf:${DB_PASSWORD}@db:5432/graaf_zeppelin
      - GRAPH_MODEL_PATH=data/models/sportdeelname_graph.json
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=graaf
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=graaf_zeppelin
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U graaf"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - web
    restart: unless-stopped

volumes:
  pgdata:
  caddy_data:
  caddy_config:
YAML
```

### 5c. Geheimen instellen

Maak een `.env` bestand aan met je wachtwoorden:

```bash
# Genereer veilige wachtwoorden
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DB_PASSWORD=${DB_PASSWORD}
EOF

# Beveilig het bestand
chmod 600 .env

# Controleer (de waardes zijn uniek voor jouw installatie)
cat .env
```

> **Bewaar deze waardes!** Als je ze kwijtraakt moet je ze opnieuw genereren (en gaat je database sessie-data verloren).

### 5d. Caddyfile aanmaken (webserver)

**Zonder domeinnaam** (alleen IP-adres):

```bash
cat > Caddyfile << 'CADDY'
:80 {
    reverse_proxy web:8000
}
CADDY
```

**Met domeinnaam** (HTTPS wordt automatisch geregeld):

```bash
cat > Caddyfile << 'CADDY'
jouwdomein.nl {
    reverse_proxy web:8000
}
CADDY
```

> Vervang `jouwdomein.nl` door je eigen domein. Caddy regelt automatisch een SSL-certificaat via Let's Encrypt.

### 5e. Starten!

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Dit duurt de eerste keer 2-3 minuten (Docker downloadt images en bouwt de app).

### 5f. Controleren of alles draait

```bash
# Alle drie containers moeten "running" zijn
docker compose -f docker-compose.prod.yml ps

# Logs bekijken
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs db

# Test of de app reageert
curl http://localhost:8000/
```

Open nu je browser en ga naar `http://JOUW_IP_ADRES`. Je zou de Graaf Zeppelin homepage moeten zien.

---

## 6. Domeinnaam koppelen (optioneel)

Als je een domeinnaam wilt (bijv. `graafzeppelin.nl`):

1. **Koop een domein** bij bijv. TransIP, Versio, of Cloudflare (~€10/jaar voor .nl)
2. Ga naar de **DNS-instellingen** van je domein
3. Voeg een **A-record** toe:

   | Type | Naam | Waarde | TTL |
   |------|------|--------|-----|
   | A | @ | JOUW_IP_ADRES | 300 |
   | A | www | JOUW_IP_ADRES | 300 |

4. Wacht 5-30 minuten tot DNS propageert
5. Pas de `Caddyfile` aan (zie stap 5d, variant "met domeinnaam")
6. Herstart Caddy:
   ```bash
   docker compose -f docker-compose.prod.yml restart caddy
   ```

Caddy regelt automatisch HTTPS via Let's Encrypt. Na 1-2 minuten werkt `https://jouwdomein.nl`.

---

## 7. HTTPS instellen

### Met domeinnaam
Al geregeld! Caddy doet dit automatisch (stap 6).

### Zonder domeinnaam (zelf-gesigneerd certificaat)
Als je geen domein hebt maar toch HTTPS wilt:

```bash
cat > Caddyfile << 'CADDY'
:443 {
    tls internal
    reverse_proxy web:8000
}

:80 {
    redir https://{host}{uri} permanent
}
CADDY
```

```bash
docker compose -f docker-compose.prod.yml restart caddy
```

> Je browser geeft een waarschuwing bij zelf-gesigneerde certificaten — dat is normaal.

---

## 8. Backups instellen

### Database backup (dagelijks)

```bash
# Maak backup-script
cat > ~/backup-db.sh << 'BASH'
#!/bin/bash
BACKUP_DIR=~/backups/postgres
mkdir -p $BACKUP_DIR
DATE=$(date +%Y-%m-%d_%H%M)
cd ~/apps/Graaf_Zeppelin

docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U graaf graaf_zeppelin | gzip > $BACKUP_DIR/graaf_$DATE.sql.gz

# Bewaar alleen de laatste 14 dagen
find $BACKUP_DIR -name "*.sql.gz" -mtime +14 -delete
echo "Backup gemaakt: graaf_$DATE.sql.gz"
BASH

chmod +x ~/backup-db.sh

# Test de backup
~/backup-db.sh
```

### Automatisch draaien (elke nacht om 3:00)

```bash
crontab -e
```

Voeg deze regel toe:
```
0 3 * * * /home/deploy/backup-db.sh >> /home/deploy/backups/backup.log 2>&1
```

### Backup terugzetten (als het nodig is)

```bash
gunzip < ~/backups/postgres/graaf_2025-01-15_0300.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db \
  psql -U graaf graaf_zeppelin
```

### Hetzner snapshots (hele server)

In de Hetzner Console kun je ook **server snapshots** inschakelen:
- Ga naar je server → Snapshots → Enable
- Kosten: €0,01/GB/mnd (een 40GB server = ~€0,40/mnd)

---

## 9. Updates deployen

Als je een nieuwe versie van Graaf Zeppelin wilt deployen:

```bash
cd ~/apps/Graaf_Zeppelin

# Haal de laatste code op
git pull origin main

# Herbouw en herstart (zero-downtime is ~10 seconden)
docker compose -f docker-compose.prod.yml up -d --build

# Controleer of alles draait
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=20 web
```

### Database migraties draaien (als er schema-wijzigingen zijn)

```bash
docker compose -f docker-compose.prod.yml exec web \
  alembic upgrade head
```

---

## 10. Problemen oplossen

### "Ik kan niet verbinden via SSH"

```bash
# Controleer of het IP-adres klopt
# Controleer of je SSH key op de juiste plek staat (~/.ssh/id_ed25519)

# Probeer met verbose output:
ssh -v root@JOUW_IP_ADRES
```

### "De website laadt niet"

```bash
# Draaien alle containers?
docker compose -f docker-compose.prod.yml ps

# Bekijk logs voor fouten
docker compose -f docker-compose.prod.yml logs web --tail=50
docker compose -f docker-compose.prod.yml logs db --tail=50
docker compose -f docker-compose.prod.yml logs caddy --tail=50

# Is poort 80/443 open?
ufw status
```

### "Database connection error"

```bash
# Draait PostgreSQL?
docker compose -f docker-compose.prod.yml exec db pg_isready -U graaf

# Klopt het wachtwoord in .env?
cat .env
```

### "Container start niet op"

```bash
# Bekijk gedetailleerde logs
docker compose -f docker-compose.prod.yml logs web

# Herbouw volledig (clean)
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### Alles opnieuw beginnen (nuclear option)

```bash
# WAARSCHUWING: dit verwijdert ook je database!
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Snel referentiekaartje

| Actie | Commando |
|-------|---------|
| Inloggen op server | `ssh deploy@IP_ADRES` |
| Status bekijken | `docker compose -f docker-compose.prod.yml ps` |
| Logs bekijken | `docker compose -f docker-compose.prod.yml logs web` |
| Herstarten | `docker compose -f docker-compose.prod.yml restart` |
| Updaten | `git pull && docker compose -f docker-compose.prod.yml up -d --build` |
| Stoppen | `docker compose -f docker-compose.prod.yml down` |
| Backup maken | `~/backup-db.sh` |
| Database shell | `docker compose -f docker-compose.prod.yml exec db psql -U graaf graaf_zeppelin` |

---

## Waarom Render niet (toelichting)

Je noemde dat Render niet lukte voor n8n. Dat klopt — Render heeft beperkingen die voor dit soort apps problematisch zijn:

| Probleem | Render | Hetzner VPS |
|----------|--------|-------------|
| **Cold starts** | Free/Starter containers slapen na 15 min inactiviteit, 30+ sec opstarttijd | Altijd aan |
| **Langlopende requests** | Timeout na 30 sec (LLM-calls duren soms langer) | Geen limiet |
| **Persistent storage** | Beperkt, verdwijnt bij redeploy op free tier | Echte disk, blijft bestaan |
| **PostgreSQL** | Apart betalen (~$7/mnd), limiet op free tier | Draait gewoon mee in Docker |
| **Kosten bij groei** | Snel duurder (Web Service $7 + DB $7 = $14/mnd) | Vast €5–9/mnd |
| **Controle** | Beperkt, geen SSH toegang | Volledige controle |

Render is prima voor een simpele static site of API zonder database, maar voor een app als Graaf Zeppelin (met PostgreSQL, langlopende LLM-calls, en persistent data) is een VPS gewoon beter geschikt.
