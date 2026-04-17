from flask import Flask, jsonify, request
import os

app = Flask(__name__)

APP_ENV     = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Dados em memória (simulando banco)
indicadores = [
    {"id": 1, "cidade": "São Paulo",    "categoria": "Energia",   "valor": 72.4, "unidade": "%"},
    {"id": 2, "cidade": "Curitiba",     "categoria": "Água",      "valor": 88.1, "unidade": "%"},
    {"id": 3, "cidade": "Manaus",       "categoria": "Resíduos",  "valor": 45.3, "unidade": "%"},
    {"id": 4, "cidade": "Porto Alegre", "categoria": "Energia",   "valor": 91.0, "unidade": "%"},
]


@app.route("/")
def home():
    return jsonify({
        "projeto": "Cidades ESG Inteligentes",
        "versao": APP_VERSION,
        "ambiente": APP_ENV,
        "status": "online",
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "ambiente": APP_ENV}), 200


@app.route("/indicadores")
def listar():
    cidade = request.args.get("cidade")
    dados = [i for i in indicadores if i["cidade"] == cidade] if cidade else indicadores
    return jsonify({"total": len(dados), "dados": dados})


@app.route("/indicadores", methods=["POST"])
def criar():
    body = request.get_json()
    if not body or "cidade" not in body or "categoria" not in body:
        return jsonify({"erro": "Campos 'cidade' e 'categoria' são obrigatórios"}), 400
    novo = {
        "id": len(indicadores) + 1,
        "cidade": body["cidade"],
        "categoria": body["categoria"],
        "valor": body.get("valor", 0),
        "unidade": body.get("unidade", "%"),
    }
    indicadores.append(novo)
    return jsonify({"mensagem": "Indicador criado", "dado": novo}), 201


@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=(APP_ENV != "production"))
