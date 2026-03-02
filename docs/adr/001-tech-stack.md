# ADR 001 — Escolha da Stack Tecnológica

**Status:** Aceito
**Data:** 2025-03-01
**Decisores:** Equipe TerremotoTracker

---

## Contexto

Precisamos construir um dashboard de monitoramento sísmico em tempo real que:
- Consuma APIs públicas externas (USGS, Smithsonian GVP)
- Exiba um mapa interativo com centenas de pins simultâneos
- Atualize dados sem recarregar a página (WebSocket)
- Seja deployável com um único comando (`docker-compose up`)

## Decisões

### Backend: FastAPI + Python

**Por quê FastAPI em vez de Django/Flask?**
- Suporte nativo a async/await — essencial para WebSockets e calls paralelas a APIs externas
- Geração automática de documentação OpenAPI (Swagger UI em `/docs`)
- Performance próxima ao Node.js para I/O bound workloads
- Type hints nativos com validação automática via Pydantic

**Rejeitados:**
- *Django*: framework muito "pesado" para uma API, ORM síncrono por padrão
- *Flask*: sem suporte async nativo, WebSockets requerem extensions externas
- *Node.js/Express*: ecossistema menos maduro para análise de dados geoespaciais

### Banco de Dados: PostgreSQL

**Por quê PostgreSQL em vez de MongoDB?**
- Dados de terremotos têm schema previsível — SQL é mais adequado que documentos flexíveis
- Queries de filtro geoespacial (lat/lon bounding box) são eficientes com índices B-tree
- PostGIS disponível caso precise de queries geoespaciais avançadas no futuro
- Transações ACID garantem integridade dos dados de alertas

### Cache: Redis

**Por quê Redis?**
- TTL nativo por chave — perfeito para cache de APIs com rate limit (60s para USGS)
- Pub/Sub para broadcasting de eventos WebSocket entre múltiplos workers (escalabilidade futura)
- Persistência opcional com RDB/AOF

### ORM: SQLAlchemy 2.0 Async + Alembic

**Por quê SQLAlchemy em vez de Tortoise-ORM ou Prisma?**
- Ecossistema mais maduro e documentado
- SQLAlchemy 2.0 tem suporte async completo com asyncpg
- Alembic é o padrão de mercado para migrations em Python
- `mapped_column` com type hints torna o código mais legível e seguro

### Frontend: React 19 + Vite + TypeScript

**Por quê React em vez de Vue/Svelte?**
- Ecossistema maior, mais bibliotecas de mapas e gráficos disponíveis
- React 19 com Concurrent Features para atualizações em tempo real mais suaves
- TypeScript elimina classe inteira de bugs em runtime

**Por quê Vite em vez de Create React App?**
- HMR (Hot Module Replacement) praticamente instantâneo
- Build 10-100x mais rápido que CRA/Webpack
- Configuração nativa de proxy para o backend

### Mapas: Leaflet + react-leaflet

**Por quê Leaflet em vez de MapboxGL ou Google Maps?**
- **100% gratuito** — sem API key, sem billing surpresa
- react-leaflet fornece abstrações React idiomáticas
- MarkerCluster nativo para agrupar centenas de pins sem degradar performance

### Gráficos: Recharts

**Por quê Recharts em vez de Chart.js ou D3?**
- API declarativa (componentes React) em vez de imperativa
- Responsivo por padrão
- Leve e sem dependências externas

### Tempo Real: WebSockets Nativos do FastAPI

**Por quê WebSockets em vez de SSE (Server-Sent Events) ou polling?**
- WebSockets são bidirecionais — permite enviar filtros do frontend para o backend no futuro
- FastAPI tem suporte nativo via Starlette, sem biblioteca adicional
- Polling a cada N segundos desperdiça recursos e tem latência previsível alta

## Consequências

**Positivas:**
- Stack moderna e bem documentada — fácil de encontrar ajuda e contratar
- Tudo open-source e gratuito — zero custo para APIs e ferramentas
- Docker Compose permite reproduzir o ambiente identicamente em qualquer máquina

**Negativas:**
- Python async tem curva de aprendizado maior que Django síncrono
- SQLAlchemy async é mais verboso que ORMs mais simples como Tortoise

## Alternativas Consideradas e Rejeitadas

| Componente | Alternativas rejeitadas | Motivo |
|---|---|---|
| Backend | Django REST Framework | ORM síncrono, overhead para API pura |
| Banco | MongoDB | Schema flexível desnecessário aqui |
| Tempo real | Polling a cada 30s | Latência alta, desperdício de recursos |
| Mapas | Google Maps | Custo a partir de 28k requests/mês |
| Gráficos | D3.js | Muito baixo nível para este caso de uso |
