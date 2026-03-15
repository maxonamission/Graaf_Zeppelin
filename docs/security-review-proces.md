# Structureel Security Review Proces — Graaf Zeppelin

> **Versie**: 1.0
> **Datum**: 15 maart 2026
> **Eigenaar**: Security Champion

---

## 1. Doel

Beveiliging is geen eenmalige actie. Dit document beschrijft hoe beveiligingsreviews structureel worden ingebed in de ontwikkelcyclus, zodat nieuwe features, dependencies en configuratiewijzigingen consequent worden getoetst.

---

## 2. Security Champion

### Rol
Eén teamlid wordt aangewezen als **Security Champion**. Dit is geen fulltime rol, maar een verantwoordelijkheid bovenop de reguliere taken.

### Taken
- Bewaakt dat de security checklist (sectie 3) wordt gevolgd bij code reviews
- Monitort Dependabot/pip-audit meldingen en coördineert patches
- Organiseert de halfjaarlijkse handmatige review en jaarlijkse pentest
- Eerste aanspreekpunt bij beveiligingsvragen van het team
- Houdt dit document en het threat model (`docs/threat-model.md`) actueel

### Aanwijzing
- **Huidige Security Champion**: [Naam invullen]
- **Backup**: [Naam invullen]
- Wissel jaarlijks om kennis te spreiden

---

## 3. Security Checklist voor Code Reviews

Gebruik deze checklist bij elke pull request die code wijzigt. Niet elk punt is altijd van toepassing — gebruik gezond verstand.

### 3.1 Authenticatie & autorisatie

- [ ] Heeft dit endpoint authenticatie nodig? Zo ja, is `get_current_user` dependency aanwezig?
- [ ] Is role-based access control nodig? Zo ja, is `require_role()` correct geconfigureerd?
- [ ] Worden resources van andere gebruikers afgeschermd? (eigendomscontrole op user_id/email)

### 3.2 Input-validatie

- [ ] Is alle gebruikersinvoer gevalideerd via Pydantic-modellen?
- [ ] Zijn er lengtelimieten op tekstvelden? (max 2000 tekens voor vraagtekst)
- [ ] Wordt pad-traversal voorkomen bij bestandspaden? (geen `../` in gebruikersinvoer)
- [ ] Worden ID's gevalideerd op type? (UUID voor conversations, int voor user_id)

### 3.3 Output & templates

- [ ] Wordt gebruikersinvoer ge-escaped in Jinja2-templates? (autoescaping staat aan, maar `|safe` omzeilt dit)
- [ ] Bevatten API-responses geen interne details (stack traces, SQL-fouten, bestandspaden)?
- [ ] Worden API-keys of wachtwoorden nergens in responses opgenomen?

### 3.4 Data & cryptografie

- [ ] Worden gevoelige gegevens (API-keys) versleuteld opgeslagen via KeyVault?
- [ ] Worden wachtwoorden uitsluitend als bcrypt-hash opgeslagen?
- [ ] Worden tokens/secrets nergens gelogd? (check log-statements)

### 3.5 Rate limiting & DoS

- [ ] Heeft dit endpoint rate limiting nodig? (alle state-wijzigende en LLM-endpoints)
- [ ] Is er een limiet op payload-grootte?
- [ ] Kan een kwaadwillende gebruiker via dit endpoint kosten genereren? (LLM-aanroepen)

### 3.6 LLM-integratie (OWASP LLM Top 10)

- [ ] Gaat gebruikersinvoer naar een LLM-prompt? Zo ja, wordt `_guard_user_input()` aangeroepen? (LLM01)
- [ ] Wordt LLM-output gesaniteerd via `sanitize_llm_output()` voordat het naar de client gaat? (LLM05)
- [ ] Bevat de systeemprompt de "nooit onthullen"-regel? (LLM07)
- [ ] Wordt de LLM-response gevalideerd tegen het causale model via `validate_response_factors()`? (LLM09)
- [ ] Zijn nieuwe LLM-interacties begrensd? (max_tokens, timeout, rate limiting) (LLM10)
- [ ] Worden geblokkeerde injection/leakage pogingen geauditlogd?

### 3.7 Dependencies

- [ ] Worden nieuwe dependencies toegevoegd? Zo ja: is de library actief onderhouden? Heeft het bekende CVE's?
- [ ] Is de dependency toegevoegd aan `requirements.txt` met minimumversie?

### 3.8 Configuratie

- [ ] Worden er nieuwe omgevingsvariabelen geïntroduceerd? Zo ja, staan ze in `.env.example`?
- [ ] Bevatten configuratiebestanden geen hardcoded secrets?

---

## 4. Jaarplanning

| Frequentie | Activiteit | Verantwoordelijke | Output |
|-----------|-----------|-------------------|--------|
| **Bij elke PR** | Security checklist (sectie 3) | Reviewer + Security Champion | Goedgekeurde PR |
| **Wekelijks** | Dependabot/pip-audit meldingen controleren | Security Champion | Patches of triage |
| **Kwartaal** | Geautomatiseerde security scan (bandit + semgrep + pip-audit) | CI/CD (automatisch) | Scan-rapport |
| **Halfjaar** | Handmatige security review van nieuwe code sinds vorige review | Security Champion + extern | Review-rapport |
| **Jaar** | Penetratietest door externe partij | Security Champion (coördinatie) | Pentest-rapport |
| **Jaar** | Tabletop exercise (incident response oefening) | Security Champion | Evaluatieverslag |
| **Jaar** | Threat model herzien | Security Champion + team | Bijgewerkt threat model |

---

## 5. Handmatige halfjaarlijkse review

### Scope
- Alle code die is gewijzigd sinds de vorige review
- Nieuwe endpoints en API-routes
- Wijzigingen in authenticatie, autorisatie of cryptografie
- Nieuwe dependencies

### Aanpak
1. `git diff --stat <vorige-review-tag>..HEAD` — overzicht van gewijzigde bestanden
2. Focus op bestanden in `app/api/`, `app/core/`, en `app/models/`
3. Controleer tegen de beveiligingsaudit (`docs/beveiligingsaudit-v2.md`) of eerdere bevindingen niet opnieuw zijn geïntroduceerd
4. Controleer het threat model (`docs/threat-model.md`) op nieuwe actoren of datstromen
5. Documenteer bevindingen en maak stories aan voor eventuele issues

### Output
Een kort verslag met:
- Datum en scope van de review
- Bevindingen (indien van toepassing)
- Conclusie: "Geen nieuwe risico's" of "Stories aangemaakt: S##-##"

---

## 6. Integratie met bestaande processen

### CI/CD pipeline (S11-05)
De volgende scans draaien automatisch:
- **bandit**: Python-specifieke security checks bij elke push
- **semgrep**: Patroonherkenning voor bekende kwetsbaarheden bij elke push
- **pip-audit**: Dependency CVE-scan per kwartaal (en op aanvraag)

### Herhalingsschema uit beveiligingsaudit-v2.md
De audit specificeert dat een herhaalde controle nodig is bij:
- Major releases
- Toevoegen van nieuwe API-endpoints
- Wijzigingen in authenticatie of autorisatie
- Wijzigingen in de database-structuur
- Integratie van nieuwe externe diensten

Dit schema is hierin opgenomen via de halfjaarlijkse review (sectie 5).

---

## 7. Herziening

Dit document wordt herzien:
- Bij wijzigingen in de ontwikkelworkflow (bijv. nieuwe CI/CD-stappen)
- Bij de jaarlijkse threat model herziening
- Wanneer de Security Champion wisselt
