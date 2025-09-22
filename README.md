# Meteostat Server (modernized)

The Meteostat server lets you run a local instance of the Meteostat JSON API. It provides endpoints which return historical weather data and meta information in JSON format.

What's new in this fork:
- Modern dependency management via pyproject.toml and uv
- Flask 3.x and SQLAlchemy 2.x compatibility
- Config via environment variables or ~/.meteostat-server/config.ini
- Health endpoint at /health
- Production-ready Dockerfile and optional docker-compose.yml

## Quick start (local)

Prerequisites:
- Python 3.10+
- uv (https://docs.astral.sh/uv/) or install via pipx: pipx install uv

Install dependencies:

```bat
uv sync
```

Run the dev server:

```bat
uv run python app.py
```

By default it listens on 0.0.0.0:8000. Test:

```bat
curl http://localhost:8000/health
```

### Configuration

You can provide configuration either via a config file or environment variables.

Option A: Config file
- Create %USERPROFILE%\.meteostat-server\config.ini (on Linux/macOS: ~/.meteostat-server/config.ini)
- Use config.example.ini as a template

Option B: Environment variables (override config file if present)
- METEOSTAT_SERVER_NAME
- METEOSTAT_SECRET_NAME, METEOSTAT_SECRET_VALUE, METEOSTAT_SECRET_DISABLE=1 to disable
- DATABASE_URL (e.g. mysql+mysqlconnector://user:pass@host:3306/db?charset=utf8)
- Or individual DB vars: METEOSTAT_DB_HOST, METEOSTAT_DB_PORT, METEOSTAT_DB_USER, METEOSTAT_DB_PASSWORD, METEOSTAT_DB_NAME

## Docker

Build image:

```bat
docker build -t meteostat-server .
```

Run container (no auth header, DB via env):

```bat
docker run --rm -p 8000:8000 ^
  -e METEOSTAT_SECRET_DISABLE=1 ^
  -e DATABASE_URL="mysql+mysqlconnector://user:pass@host:3306/meteostat?charset=utf8" ^
  meteostat-server
```

Test:

```bat
curl http://localhost:8000/health
```

### Docker Compose (with MySQL)

A sample compose file is included. It starts MySQL and the API:

```bat
docker compose up -d --build
```

This exposes:
- API at http://localhost:8000
- MySQL on port 3306 (credentials in docker-compose.yml)

## Production

For production, prefer running the container image (it uses gunicorn by default). If deploying on your own stack, point a reverse proxy to the container and configure secrets/DB access via environment variables.

## Data License

Meteorological data is provided under the terms of the Creative Commons Attribution-NonCommercial 4.0 International Public License (CC BY-NC 4.0). You may build upon the material for any purpose, even commercially. However, you are not allowed to redistribute Meteostat data "as-is" for commercial purposes.

## Code License

The code of the Meteostat project is available under the MIT license.
