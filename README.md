# 🌋 TerremotoTracker

[![CI](https://github.com/sasse1910/TerremotoTracker/actions/workflows/ci.yml/badge.svg)](https://github.com/sasse1910/TerremotoTracker/actions)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> Monitor em tempo real de terremotos e vulcões ativos no mundo, usando exclusivamente APIs públicas e gratuitas.

## Features

- **Mapa interativo** com pins clusterizados coloridos por magnitude
- **Dados em tempo real** via WebSocket (sem recarregar a página)
- **Filtros dinâmicos**: magnitude mínima, período (24h / 7d / 30d), tipo
- **Dashboard KPI**: total de eventos, maior magnitude, região mais ativa
- **Alertas críticos**: banner vermelho pulsando para eventos M>6.0
- **Gráficos**: frequência diária e distribuição por magnitude
- **Zero custo**: apenas APIs públicas (USGS, Smithsonian GVP)

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI 0.115 + Python 3.12 |
| Banco de dados | PostgreSQL 16 |
| Cache | Redis 7 (TTL 60s) |
| ORM / Migrations | SQLAlchemy 2.0 async + Alembic |
| Frontend | React 19 + Vite + TypeScript |
| Mapas | Leaflet + react-leaflet + MarkerCluster |
| Gráficos | Recharts |
| Estilo | Tailwind CSS 3 |
| Tempo real | WebSockets nativos (FastAPI/Starlette) |
| Infra | Docker Compose |
| CI/CD | GitHub Actions |

## Início Rápido

### Pré-requisitos

- Docker 24+ e Docker Compose v2
- Git

### 1. Clone e configure

```bash
git clone https://github.com/SEU_USUARIO/TerremotoTracker.git
cd TerremotoTracker

# Cria o .env a partir do template
cp .env.example .env
```

> **Importante:** O `.env` já vem com valores funcionais para desenvolvimento.
> Troque `SECRET_KEY` e as senhas antes de fazer deploy em produção.

### 2. Suba tudo com um comando

```bash
docker-compose up --build
```

Aguarde cerca de 30–60s na primeira vez (download das imagens + compilação).

### 3. Acesse

| Serviço | URL |
|---|---|
| **Frontend** | http://localhost:5173 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **pgAdmin** | http://localhost:5050 |
| **Health Check** | http://localhost:8000/health |

## Estrutura do Projeto

```
TerremotoTracker/
├── backend/               # FastAPI + Python
│   ├── app/
│   │   ├── api/v1/        # Rotas REST e WebSocket
│   │   ├── core/          # Config, DB, Redis, Logging
│   │   ├── models/        # SQLAlchemy ORM
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Integração com USGS/GVP
│   ├── alembic/           # Migrations de banco
│   └── tests/             # pytest (cobertura >80%)
├── frontend/              # React + Vite + TypeScript
│   └── src/
│       ├── components/    # Componentes React
│       ├── hooks/         # Custom hooks
│       ├── services/      # Axios + WebSocket client
│       └── store/         # Zustand (estado global)
├── docs/
│   ├── adr/               # Architecture Decision Records
│   └── architecture.md   # Diagrama do sistema
└── .github/workflows/     # CI com pytest + lint
```

## Endpoints da API

```
GET  /health                    Status da aplicação
GET  /health/detailed           Status com verificação de DB e Redis

GET  /api/v1/earthquakes        Lista terremotos com filtros
GET  /api/v1/earthquakes/{id}   Detalhe de um terremoto
GET  /api/v1/volcanoes          Lista vulcões ativos

WS   /ws/live                   Stream de eventos em tempo real
```

**Parâmetros de filtro para `/earthquakes`:**
```
?min_magnitude=5.0              Magnitude mínima
?period=24h|7d|30d              Período de tempo
?bbox=-180,-90,180,90           Bounding box geográfico (lon_min,lat_min,lon_max,lat_max)
```

## Desenvolvimento Local (sem Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure DATABASE_URL e REDIS_URL no .env apontando para localhost
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev
```

## Testes

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

## Decisões de Arquitetura

Veja [docs/adr/001-tech-stack.md](docs/adr/001-tech-stack.md) para as decisões técnicas documentadas.

## APIs Utilizadas

- **USGS Earthquake Hazards Program** — https://earthquake.usgs.gov/fdsnws/event/1
- **Smithsonian Global Volcanism Program** — https://volcano.si.edu
- **Open-Meteo** — https://open-meteo.com (dados meteorológicos futuros)

Todas são públicas, gratuitas e sem necessidade de API key.

## Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feat/nome-da-feature`
3. Commit com mensagem semântica: `git commit -m "feat: adiciona filtro por país"`
4. Push e abra um Pull Request

## Licença

MIT — veja [LICENSE](LICENSE) para detalhes.
