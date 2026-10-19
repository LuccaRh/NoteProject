"""Testes do hook de foco: python3 -m unittest tools/test_foco.py"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foco  # noqa: E402

ESCOPO = """---
id: add-sync
nome: Sync com o servidor
areas: [sync]
---
## Pedido
1. Daemon manda updates Yjs ao servidor
## Contexto
- Auth: só o token fixo de teste
## Fora
- Tela de login
"""


class TestFoco(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / "kb" / "escopos").mkdir(parents=True)
        self.estado = self.raiz / "build" / "foco"

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, prompt, branch, juiz=lambda *a: ("pedido", "")):
        ev = {"prompt": prompt, "session_id": "s"}
        return foco.contexto(ev, self.raiz, self.estado, juiz, branch)

    def test_master_e_comando_nao_avisam(self):
        self.assertIsNone(self.rodar("faz a tela de login", "master"))
        self.assertIsNone(self.rodar("/commit", "add-sync"))

    def test_sem_escopo_pede_uma_vez(self):
        r = self.rodar("bora", "add-sync")
        self.assertIn("/foco", r["hookSpecificOutput"]["additionalContext"])
        self.assertIsNone(self.rodar("de novo", "add-sync"))

    def test_juiz(self):
        (self.raiz / "kb" / "escopos" / "add-sync.md").write_text(ESCOPO)
        self.assertIsNone(self.rodar("manda o update", "add-sync"))
        r = self.rodar("faz a tela de login", "add-sync", lambda *a: ("fora", "login está em Fora"))
        self.assertIn("⚠ Foco (add-sync, fora)", r["systemMessage"])

    def test_branch_com_barra(self):
        self.assertEqual(foco.arquivo_escopo("feat/x", self.raiz).name, "feat__x.md")


if __name__ == "__main__":
    unittest.main()
