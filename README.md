# 🌿 Cidades ESG Inteligentes

> API REST para monitoramento de indicadores de sustentabilidade (ESG) de cidades brasileiras.

![Pipeline](https://github.com/Marcosvilel/cidades-esg-inteligentes/actions/workflows/ci-cd.yml/badge.svg)

| Ambiente | URL | Status |
|----------|-----|--------|
| 🟡 Staging | https://cidades-esg-inteligentes-staging.up.railway.app | Online |
| 🟡 Staging | https://cidades-esg-inteligentes-staging.up.railway.app/indicadores | Online |
| 🟢 Produção | https://cidades-esg-inteligentes-production-d18d.up.railway.app | Online |
| 🟢 Produção | https://cidades-esg-inteligentes-production-d18d.up.railway.app/indicadores | Online |

---

## 📋 Sumário

- [Como executar localmente](#-como-executar-localmente-com-docker)
- [Pipeline CI/CD](#-pipeline-cicd)
- [Containerização](#-containerização)
- [Endpoints da API](#-endpoints-da-api)
- [Prints do funcionamento](#-prints-do-funcionamento)
- [Tecnologias utilizadas](#-tecnologias-utilizadas)
- [Checklist de Entrega](#-checklist-de-entrega)

---

## 🐳 Como executar localmente com Docker

### Pré-requisitos

- Docker 24+
- Docker Compose 2+
- Python 3.12+ (apenas para rodar os testes localmente)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/Marcosvilel/cidades-esg-inteligentes.git
cd cidades-esg-inteligentes

# 2. Configure as variáveis de ambiente
cp .env.example .env

# 3. Suba os containers
docker compose up -d

# 4. Verifique se está funcionando
curl http://localhost:5000/health
# Resposta esperada: {"status": "healthy", "ambiente": "staging"}

# 5. Acesse os indicadores
curl http://localhost:5000/indicadores
```

### Comandos úteis com Make

```bash
make build          # Build da imagem Docker
make up             # Sobe todos os serviços
make down           # Para todos os serviços
make test           # Executa os testes unitários
make logs           # Exibe logs em tempo real
make clean          # Remove containers e volumes
```

---

## ⚙️ Pipeline CI/CD

**Ferramenta:** GitHub Actions — `.github/workflows/ci-cd.yml`  
**Deploy:** Railway (staging + produção)

### Fluxo de branches
develop ──► (staging)
main    ──► (produção)

### Etapas do pipeline

| # | Job | Tempo | O que executa |
|---|-----|-------|---------------|
| 1 | 🧪 Build e Testes | ~10s | Instala dependências e executa 14 testes unitários |
| 2 | 🐳 Build da Imagem Docker | ~30s | Build multi-stage e push para Docker Hub |
| 3 | 🚀 Deploy Staging | ~45s | Redeploy via API Railway + health check |
| 4 | 🚀 Deploy Produção | ~45s | Redeploy via API Railway + health check |

### Como funciona

1. **Todo push** dispara os 4 jobs em sequência
2. Se os **testes falharem** (Job 1), os demais jobs são cancelados
3. O **Job 3** atualiza o ambiente de staging automaticamente
4. O **Job 4** atualiza o ambiente de produção automaticamente

### Secrets necessários

| Secret | Descrição |
|--------|-----------|
| `DOCKERHUB_USER` | Usuário Docker Hub |
| `DOCKERHUB_TOKEN` | Token Read & Write Docker Hub |
| `RAILWAY_TOKEN` | Token da API do Railway |
| `RAILWAY_SERVICE_ID` | ID do serviço de produção |
| `RAILWAY_STAGING_SERVICE_ID` | ID do serviço de staging |
| `RAILWAY_URL` | URL de produção |
| `RAILWAY_STAGING_URL` | URL de staging |

---

## 📦 Containerização

### Dockerfile (Multi-Stage)

```dockerfile
# ── Stage 1: builder ──────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ── Stage 2: produção ─────────────────────────────────────
FROM python:3.12-slim AS production

# Usuário não-root para segurança
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --create-home appuser

COPY --from=builder /install /usr/local
COPY src/ .

ENV APP_ENV=production APP_VERSION=1.0.0
USER appuser
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

### Estratégias adotadas

| Estratégia | Benefício |
|-----------|-----------|
| Multi-stage build | Imagem final ~60% menor — gcc não vai para produção |
| Usuário não-root (UID 1001) | Segurança em ambiente de produção |
| HEALTHCHECK nativo | Docker reinicia o container automaticamente se falhar |
| .dockerignore | Exclui testes, .env e .git da imagem |
| Gunicorn | Servidor WSGI robusto para produção |

### Arquitetura dos serviços
Internet │ ▼ ┌─────────────────────────┐ │ app (Flask/Gunicorn) │ porta 5000 │ rede: frontend+backend │ └────────┬─────────────────┘ │ ┌────────▼─────────────────┐ rede: backend (isolado) │ postgres :5432          │ volume: postgres_data │ redis     :6379          │ volume: redis_data └──────────────────────────┘

---

## 🔌 Endpoints da API

| Método | Endpoint | Descrição | Resposta |
|--------|----------|-----------|----------|
| GET | `/` | Status da aplicação | 200 + JSON |
| GET | `/health` | Health check | 200 `{"status":"healthy"}` |
| GET | `/ready` | Readiness probe | 200 `{"status":"ready"}` |
| GET | `/indicadores` | Lista todos os indicadores | 200 + lista |
| GET | `/indicadores?cidade=X` | Filtra por cidade | 200 + lista filtrada |
| POST | `/indicadores` | Cria novo indicador | 201 + objeto criado |

### Exemplo de resposta — `/indicadores`

```json
{
  "total": 4,
  "dados": [
    {"id": 1, "cidade": "São Paulo",    "categoria": "Energia",  "valor": 72.4, "unidade": "%"},
    {"id": 2, "cidade": "Curitiba",     "categoria": "Água",     "valor": 88.1, "unidade": "%"},
    {"id": 3, "cidade": "Manaus",       "categoria": "Resíduos", "valor": 45.3, "unidade": "%"},
    {"id": 4, "cidade": "Porto Alegre", "categoria": "Energia",  "valor": 91.0, "unidade": "%"}
  ]
}
```

---

## 🖥️ Prints do funcionamento
<img src="Assets/Captura de tela 2026-04-17 162648.png" width="500">
<img src="Assets/Captura de tela 2026-04-17 162718.png" width="500">
<img src="Assets/Captura de tela 2026-04-17 162730.png" width="500">
<img src="Assets/Captura de tela 2026-04-17 162805.png" width="500">
### Pipeline GitHub Actions — 4 jobs verdes
Run #14 — Status: Success — 1m 26s
✅ 1 - Build e Testes         7s
✅ 2 - Build da Imagem Docker  28s
✅ 3 - Deploy Staging          42s
✅ 4 - Deploy Producao         43s

### Testes locais — 14/14 passando
test_health_200 ..................... ok
test_health_status .................. ok
test_ready_200 ...................... ok
test_home_200 ....................... ok
test_home_ambiente_testing .......... ok
test_home_json ...................... ok
test_home_status_online ............. ok
test_criar_indicador ................ ok
test_criar_sem_campos ............... ok
test_criar_sem_json ................. ok
test_filtrar_por_cidade ............. ok
test_listar_todos ................... ok
test_metodo_nao_permitido ........... ok
test_rota_inexistente ............... ok
Executou 14 testes em 0,013s — OK

### Ambientes online

| Ambiente | Endpoint | Resposta |
|----------|----------|----------|
| Staging | `/health` | `{"ambiente":"production","status":"healthy"}` |
| Produção | `/health` | `{"ambiente":"production","status":"healthy"}` |

---

## 🛠️ Tecnologias utilizadas

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Linguagem | Python | 3.12 |
| Framework web | Flask | 3.0.3 |
| Servidor WSGI | Gunicorn | 22.0 |
| Banco de dados | PostgreSQL | 16-alpine |
| Cache | Redis | 7.2-alpine |
| Containerização | Docker (multi-stage) | 24+ |
| Orquestração | Docker Compose | 2+ |
| CI/CD | GitHub Actions | — |
| Deploy | Railway | — |
| Testes | unittest (stdlib) | — |

---

## ✅ Checklist de Entrega

| Item | Status |
|------|--------|
| Projeto compactado em .ZIP com estrutura organizada | ✅ |
| Dockerfile funcional (multi-stage) | ✅ |
| docker-compose.yml com volumes, redes e variáveis de ambiente | ✅ |
| Pipeline com etapas de build, teste e deploy | ✅ |
| README.md com instruções e prints | ✅ |
| Documentação técnica com evidências (PDF) | ✅ |
| Deploy realizado nos ambientes staging e produção | ✅ |

