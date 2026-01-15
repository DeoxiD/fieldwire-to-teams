# Fieldwire to Teams Integration

Automātiski nosūta Fieldwire Task atjauninājumus ar pievienotajām fotogrāfijām uz Microsoft Teams kanālu. Modulārs, konfiguējams, adaptīvs Python projekts ar JWT autentifikāciju, Adaptive Cards un schedule integrāciju.

## Iespējas

✅ **JWT Autentifikācija** - Draudzīga autentifikācija ar Fieldwire API
✅ **Adaptive Cards** - Skaisti formatēti Team sūtījumi ar fotiem
✅ **Periodiski Polling** - Automātiski pārbaudīt jaunos Task atjauninājumus
✅ **Modulāra Arhitektūra** - auth.py, fetch.py, send.py, card.py
✅ **Jinja2 Templāti** - Viegli pielāgojams Adaptive Card dizains
✅ **Docker Atbalsts** - Containerizācija ražošanas videi
✅ **Dry-Run Režīms** - Testēt bez nosūtīšanas uz Teams
✅ **Pilnīgi Dokumentēts** - Komentāri, README, examples

## Prasības

- Python 3.8+
- Fieldwire API token
- Microsoft Teams Incoming Webhook URL
- requests, python-dotenv, jinja2, schedule bibliotēkas

## Instalēšana

### 1. Klonējiet repozitoriju

```bash
git clone https://github.com/DeoxiD/fieldwire-to-teams.git
cd fieldwire-to-teams
```

### 2. Instalējiet dependences

```bash
pip install -r requirements.txt
```

### 3. Konfigurējiet .env failu

```bash
cp .env.example .env
```

Rediģējiet `.env` failā un pievienojiet:
- `FIELDWIRE_API_TOKEN` - Jūsu API token
- `TEAMS_WEBHOOK_URL` - Jūsu Teams Webhook URL
- `FIELDWIRE_PROJECT_IDS` - Projektu ID

### 4. Palaidiet skriptu

```bash
python fieldwire_to_teams.py
```

## Failu Struktūra

```
fieldwire-to-teams/
├── fieldwire_to_teams.py      # Galvenā aplikācija
├── requirements.txt             # Python dependences
├── .env.example                 # Konfigurācijas piemērs
├── Dockerfile                   # Docker container
├── modules/
│   ├── __init__.py
│   ├── auth.py                 # JWT autentifikācija
│   ├── fetch.py                # Fieldwire API dati
│   ├── card.py                 # Adaptive Card ģenerēšana
│   └── send.py                 # Teams nosūtīšana
├── templates/
│   └── card.json.j2            # Adaptive Card šablons
└── tests/
    └── test_integration.py     # Integrācijas testi
```

## Konfigurācija

### .env Mainīgie

```env
# Fieldwire API
FIELDWIRE_API_TOKEN=your_api_token_here
FIELDWIRE_REGION=us              # us vai eu
FIELDWIRE_PROJECT_IDS=ALL        # ALL vai proj1,proj2,proj3

# Teams
TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/...

# Polling
POLL_MINUTES=5
MAX_TASKS=10

# Režīmi
DRY_RUN=false
DEBUG=false
```

## Lietošana

### Parastā palaišana

```bash
python fieldwire_to_teams.py
```

### Dry-Run tests

```bash
DRY_RUN=true python fieldwire_to_teams.py
```

### Debug režīms

```bash
DEBUG=true python fieldwire_to_teams.py
```

### Docker

```bash
docker build -t fieldwire-to-teams .
docker run -e FIELDWIRE_API_TOKEN=... -e TEAMS_WEBHOOK_URL=... fieldwire-to-teams
```

## API Integrācija

Projekts izmanto:
- **Fieldwire API v3** (JWT autentifikācija)
- **Microsoft Teams Adaptive Cards** (nosūtīšana)
- **Schedule bibliotēka** (periodiski polling)

## Kļūdu Apstrāde

- 401 Unauthorized - pārbaudiet API token
- 429 Too Many Requests - samaziniet POLL_MINUTES
- 404 Not Found - pārbaudiet PROJECT_IDS

## Attīstīšana

```bash
# Instalējiet dev dependences
pip install pytest pytest-cov

# Palaidiet testus
pytest tests/

# Ar coverage
pytest --cov=modules tests/
```

## Licence

MIT

## Autors

DeoxiD (2026)
