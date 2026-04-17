import unittest
import json
import os
import sys

os.environ["APP_ENV"]     = "testing"
os.environ["APP_VERSION"] = "1.0.0-test"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.app import app


class TestHome(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.c = app.test_client()

    def test_home_200(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)

    def test_home_json(self):
        r = self.c.get("/")
        d = json.loads(r.data)
        self.assertIn("projeto", d)
        self.assertIn("status", d)

    def test_home_status_online(self):
        r = self.c.get("/")
        d = json.loads(r.data)
        self.assertEqual(d["status"], "online")

    def test_home_ambiente_testing(self):
        r = self.c.get("/")
        d = json.loads(r.data)
        self.assertEqual(d["ambiente"], "testing")


class TestHealth(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.c = app.test_client()

    def test_health_200(self):
        r = self.c.get("/health")
        self.assertEqual(r.status_code, 200)

    def test_health_status(self):
        r = self.c.get("/health")
        d = json.loads(r.data)
        self.assertEqual(d["status"], "healthy")

    def test_ready_200(self):
        r = self.c.get("/ready")
        self.assertEqual(r.status_code, 200)


class TestIndicadores(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.c = app.test_client()

    def test_listar_todos(self):
        r = self.c.get("/indicadores")
        self.assertEqual(r.status_code, 200)
        d = json.loads(r.data)
        self.assertIn("dados", d)
        self.assertIn("total", d)
        self.assertGreater(d["total"], 0)

    def test_filtrar_por_cidade(self):
        r = self.c.get("/indicadores?cidade=Curitiba")
        d = json.loads(r.data)
        self.assertTrue(all(i["cidade"] == "Curitiba" for i in d["dados"]))

    def test_criar_indicador(self):
        payload = {"cidade": "Brasília", "categoria": "Mobilidade", "valor": 60.0}
        r = self.c.post("/indicadores", json=payload)
        self.assertEqual(r.status_code, 201)
        d = json.loads(r.data)
        self.assertEqual(d["dado"]["cidade"], "Brasília")

    def test_criar_sem_campos(self):
        r = self.c.post("/indicadores", json={})
        self.assertEqual(r.status_code, 400)

    def test_criar_sem_json(self):
        r = self.c.post("/indicadores", data="texto", content_type="text/plain")
        self.assertIn(r.status_code, [400, 415])

    def test_metodo_nao_permitido(self):
        r = self.c.delete("/indicadores")
        self.assertEqual(r.status_code, 405)

    def test_rota_inexistente(self):
        r = self.c.get("/nao-existe")
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
