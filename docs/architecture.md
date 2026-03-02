# Arquitetura do Sistema — TerremotoTracker

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO (Browser)                           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    React 19 + Vite + TypeScript               │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │  │
│  │  │  Leaflet Map │  │   Recharts    │  │  Alert Banner    │  │  │
│  │  │  (pins +     │  │  (frequency + │  │  (WebSocket      │  │  │
│  │  │  clusters)   │  │  magnitude)   │  │  triggered)      │  │  │
│  │  └──────────────┘  └───────────────┘  └──────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────┐    ┌────────────────────────────────┐  │  │
│  │  │  Sidebar Filters │    │    KPI Dashboard               │  │  │
│  │  │  (mag/period/    │    │    (total 24h, max mag,        │  │  │
│  │  │   type)          │    │     most active region)        │  │  │
│  │  └──────────────────┘    └────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│        │ HTTP (REST)                    │ WebSocket (/ws/live)      │
└────────┼────────────────────────────────┼───────────────────────────┘
         │                                │
         ▼                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI (Python 3.12)                          │
│                      porta 8000                                     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    API Router /api/v1                        │   │
│  │                                                             │   │
│  │  GET /earthquakes    GET /earthquakes/{id}                  │   │
│  │  GET /volcanoes      GET /health/detailed                   │   │
│  │                                                             │   │
│  │  Filtros: ?min_magnitude=5.0&period=7d&bbox=lon,lat,lon,lat │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────┐  ┌─────────────────────────────────────┐ │
│  │  EarthquakeService   │  │  WebSocket Manager                  │ │
│  │  (httpx async)       │  │  (broadcast para clientes ativos)   │ │
│  │                      │  │                                     │ │
│  │  USGS API → parse    │  │  Evento novo → todos os browsers    │ │
│  │  → cache → DB        │  │  conectados recebem automaticamente │ │
│  └──────────────────────┘  └─────────────────────────────────────┘ │
└───────────────────────┬─────────────────────┬───────────────────────┘
                        │                     │
           ┌────────────▼────────┐   ┌────────▼────────────┐
           │    PostgreSQL 16    │   │     Redis 7          │
           │    porta 5432       │   │     porta 6379       │
           │                     │   │                     │
           │  earthquakes        │   │  Cache TTL 60s:      │
           │  volcanoes          │   │  "earthquakes:24h"   │
           │  alerts             │   │  "earthquakes:7d"    │
           └─────────────────────┘   │  "volcanoes:all"     │
                                     └─────────────────────┘
                        │
           ┌────────────▼────────────────────────────────────┐
           │            APIs Externas (Públicas)              │
           │                                                  │
           │  USGS Earthquake API — GeoJSON Feed              │
           │  https://earthquake.usgs.gov/...                 │
           │  Rate limit: sem limite explícito, TTL 60s cache │
           │                                                  │
           │  Smithsonian GVP — Vulcões Ativos                │
           │  https://volcano.si.edu/api                      │
           │  TTL 3600s cache (dados mudam raramente)         │
           └──────────────────────────────────────────────────┘
```

## Fluxo de Dados — Request de Terremotos

```
Browser                FastAPI              Redis           PostgreSQL        USGS
  │                      │                    │                 │               │
  │── GET /earthquakes ──►│                    │                 │               │
  │                      │── GET cache key ──►│                 │               │
  │                      │◄── cache HIT? ─────│                 │               │
  │                      │                    │                 │               │
  │   [Se cache MISS]    │                    │                 │               │
  │                      │─────────────────── GET from DB ─────►│               │
  │                      │◄──────────────────── rows ───────────│               │
  │                      │                    │                 │               │
  │   [Se DB vazio/stale]│                    │                 │               │
  │                      │────────────────────────── fetch GeoJSON ────────────►│
  │                      │◄─────────────────────────── 200 OK ─────────────────│
  │                      │── upsert rows ──────────────────────►│               │
  │                      │── SET cache ───────►│                 │               │
  │                      │                    │                 │               │
  │◄─── JSON response ───│                    │                 │               │
```

## Fluxo de Dados — WebSocket em Tempo Real

```
Browser A       Browser B           FastAPI            USGS Poller (background)
   │               │                   │                        │
   │── WS connect ►│                   │                        │
   │               │── WS connect ────►│                        │
   │               │                   │                        │
   │               │                   │◄─── novo evento ───────│
   │               │                   │     (polling a cada    │
   │               │                   │      30 segundos)      │
   │               │                   │                        │
   │◄── broadcast ─┼───────────────────│                        │
   │               │◄── broadcast ─────│                        │
   │ mapa atualiza │   mapa atualiza   │                        │
```

## Estrutura de Pastas

```
TerremotoTracker/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Rotas HTTP
│   │   ├── core/                # Config, DB, Redis, Logging
│   │   ├── models/              # SQLAlchemy ORM
│   │   ├── schemas/             # Pydantic (validação I/O)
│   │   └── services/            # Lógica de negócio + USGS client
│   ├── alembic/                 # Migrations de banco
│   └── tests/                   # pytest
├── frontend/
│   └── src/
│       ├── components/          # React components
│       ├── hooks/               # Custom hooks (useWebSocket, etc.)
│       ├── services/            # API client (axios)
│       └── store/               # Zustand (estado global)
├── docs/
│   ├── adr/                     # Architecture Decision Records
│   └── architecture.md          # Este arquivo
└── .github/workflows/           # CI/CD com GitHub Actions
```
