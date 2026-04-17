.PHONY: help build up down test logs shell clean deploy-staging deploy-prod

help:
	@echo ""
	@echo "  Cidades ESG Inteligentes — Comandos disponíveis"
	@echo ""
	@echo "  make build          Build da imagem Docker"
	@echo "  make up             Sobe todos os serviços (staging)"
	@echo "  make down           Para todos os serviços"
	@echo "  make test           Executa os testes unitários"
	@echo "  make logs           Exibe logs em tempo real"
	@echo "  make shell          Shell dentro do container app"
	@echo "  make clean          Remove containers e volumes"
	@echo "  make deploy-staging Deploy no ambiente staging"
	@echo "  make deploy-prod    Deploy no ambiente produção"
	@echo ""

build:
	docker compose build --no-cache

up:
	docker compose up -d
	@echo "✅ App disponível em http://localhost:5000"

down:
	docker compose down

test:
	python -m unittest tests/test_app.py -v

logs:
	docker compose logs -f app

shell:
	docker compose exec app /bin/sh

clean:
	docker compose down -v --remove-orphans
	@echo "🧹 Ambiente limpo"

deploy-staging:
	docker compose pull app
	docker compose up -d --no-deps app
	@echo "🚀 Deploy Staging concluído"

deploy-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml pull app
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps app
	@echo "🚀 Deploy Produção concluído"
