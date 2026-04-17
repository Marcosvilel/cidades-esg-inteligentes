# Projeto — Cidades ESG Inteligentes

API REST para monitoramento de indicadores ESG (Energia, Água, Resíduos) de cidades brasileiras.

---

## Como executar localmente com Docker

### Pré-requisitos
- Docker 24+
- Docker Compose 2+

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/cidades-esg.git
cd cidades-esg

# 2. Configure as variáveis de ambiente
cp .env.example .env

# 3. Suba os containers
docker compose up -d

# 4. Verifique se está funcionando
curl http://localhost:5000/health
# Resposta: {"status": "healthy", "ambiente": "staging"}

# 5. Acesse os indicadores
curl http://localhost:5000/indicadores
```

### Comandos úteis

```bash
docker compose ps          # status dos containers
docker compose logs -f app # logs da aplicação
docker compose down        # parar tudo
docker compose down -v     # parar e remover volumes
```

---

## Pipeline CI/CD

**Ferramenta:** GitHub Actions (`.github/workflows/ci-cd.yml`)

### Estratégia de branches

```
feature/* ──► develop ──► main
                │              │
           Staging        Produção
```

### Etapas do pipeline

| # | Job | Gatilho | O que faz |
|---|-----|---------|-----------|
| 1 | Build & Testes | todo push/PR | instala deps, roda 14 testes unitários |
| 2 | Docker Build | após job 1 (não PR) | build + push da imagem no Docker Hub |
| 3 | Deploy Staging | branch `develop` | SSH no servidor, `docker compose up` |
| 4 | Deploy Produção | branch `main` | SSH no servidor, compose com override prod |

### Funcionamento

1. **Push na branch `develop`** → jobs 1, 2 e 3 rodam em sequência. O deploy no staging só acontece se os testes passarem.
2. **Push na branch `main`** (via Pull Request aprovado) → jobs 1, 2 e 4. Deploy em produção com 2 réplicas.
3. **Pull Request** → apenas job 1 roda (testes), sem deploy.

### Secrets necessários no repositório

| Secret | Descrição |
|--------|-----------|
| `DOCKERHUB_USER` | Usuário Docker Hub |
| `DOCKERHUB_TOKEN` | Token de acesso Docker Hub |
| `STAGING_HOST` | IP do servidor de staging |
| `STAGING_USER` | Usuário SSH staging |
| `STAGING_SSH_KEY` | Chave privada SSH staging |
| `PROD_HOST` | IP do servidor de produção |
| `PROD_USER` | Usuário SSH produção |
| `PROD_SSH_KEY` | Chave privada SSH produção |

---

## Containerização

### Estrutura do Dockerfile

```dockerfile
# Stage 1: builder — instala dependências
FROM python:3.12-slim AS builder
COPY src/requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: produção — imagem final enxuta
FROM python:3.12-slim AS production
COPY --from=builder /install /usr/local   # copia só os pacotes
COPY src/ .
USER appuser   # usuário não-root (UID 1001)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

### Estratégias adotadas

- **Multi-stage build** — imagem final não carrega o compilador gcc (~60% menor)
- **Usuário não-root** — segurança em produção (UID/GID 1001)
- **HEALTHCHECK nativo** — Docker verifica `/health` a cada 30s automaticamente
- **Variáveis de ambiente** — zero configuração hardcoded na imagem
- **.dockerignore** — exclui testes, `.env`, `.git` da imagem final

### Serviços orquestrados

```
┌─────────────────────────────────────┐
│         rede: frontend              │
│  ┌─────────────────────────────┐   │
│  │   app (Flask / Gunicorn)    │   │
│  │   porta 5000                │   │
│  └──────────────┬──────────────┘   │
└─────────────────┼───────────────────┘
                  │
┌─────────────────┼───────────────────┐
│         rede: backend               │
│  ┌───────────┐  │  ┌─────────────┐ │
│  │ postgres  │  │  │    redis    │ │
│  │ :5432     │  │  │    :6379    │ │
│  │ volume ✓  │  │  │  volume ✓  │ │
│  └───────────┘     └─────────────┘ │
└─────────────────────────────────────┘
```

---

## Prints do funcionamento

### Testes locais — 14/14 passando

```
test_health_200 ... ok
test_health_status ... ok
test_ready_200 ... ok
test_home_200 ... ok
test_home_ambiente_testing ... ok
test_home_json ... ok
test_home_status_online ... ok
test_criar_indicador ... ok
test_criar_sem_campos ... ok
test_criar_sem_json ... ok
test_filtrar_por_cidade ... ok
test_listar_todos ... ok
test_metodo_nao_permitido ... ok
test_rota_inexistente ... ok

Ran 14 tests in 0.025s — OK
```

### Endpoint `/` — Staging

```json
{
  "projeto": "Cidades ESG Inteligentes",
  "versao": "1.0.0",
  "ambiente": "staging",
  "status": "online"
}
```

### Endpoint `/indicadores`

```json
{
  "total": 4,
  "dados": [
    {"id": 1, "cidade": "São Paulo", "categoria": "Energia", "valor": 72.4},
    {"id": 2, "cidade": "Curitiba", "categoria": "Água", "valor": 88.1}
  ]
}
```

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12 |
| Framework web | Flask 3.0 |
| Servidor WSGI | Gunicorn |
| Banco de dados | PostgreSQL 16 |
| Cache | Redis 7.2 |
| Containerização | Docker (multi-stage) |
| Orquestração | Docker Compose |
| CI/CD | GitHub Actions |
| Testes | unittest (stdlib) |

---

## Checklist de Entrega

| Item | Status |
|------|--------|
| Projeto compactado em .ZIP com estrutura organizada | ✅ |
| Dockerfile funcional (multi-stage) | ✅ |
| docker-compose.yml com volumes, redes e variáveis | ✅ |
| Pipeline com etapas de build, teste e deploy | ✅ |
| README.md com instruções e prints | ✅ |
| Documentação técnica com evidências (PDF) | ✅ |
| Deploy configurado para staging e produção | ✅ |
