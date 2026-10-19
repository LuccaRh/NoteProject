import json, tempfile, unittest
from pathlib import Path

import hooks_contexto as h


def log(tmp, ctx):
    p = Path(tmp) / "s.jsonl"
    u = {"input_tokens": 2, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": ctx - 1002,
         "output_tokens": 50}
    p.write_text(json.dumps({"type": "user", "message": {"content": "oi"}}) + "\n"
                 + json.dumps({"type": "assistant", "message": {"id": "m1", "usage": u}}) + "\n")
    return str(p)


class AvisoClear(unittest.TestCase):
    def test_abaixo_do_limiar_nao_avisa(self):
        with tempfile.TemporaryDirectory() as t:
            ev = {"session_id": "a", "transcript_path": log(t, 50_000)}
            self.assertIsNone(h.aviso_clear(ev, Path(t) / "e"))

    def test_avisa_uma_vez_por_limiar(self):
        with tempfile.TemporaryDirectory() as t:
            e = Path(t) / "e"
            ev = {"session_id": "a", "transcript_path": log(t, 150_000)}
            self.assertIn("150k", h.aviso_clear(ev, e)["systemMessage"])
            self.assertIsNone(h.aviso_clear(ev, e))
            ev["transcript_path"] = log(t, 210_000)
            self.assertIn("/clear", h.aviso_clear(ev, e)["systemMessage"])


class Leitura(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.dir = Path(self.t.name)
        (self.dir / "grande.tex").write_text("x\n" * 900)
        (self.dir / "pequeno.md").write_text("x\n" * 50)

    def tearDown(self):
        self.t.cleanup()

    def negado(self, nome, ent):
        r = h.leitura({"tool_name": nome, "tool_input": ent, "cwd": str(self.dir)})
        return bool(r) and r["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_read(self):
        self.assertTrue(self.negado("Read", {"file_path": str(self.dir / "grande.tex")}))
        self.assertFalse(self.negado("Read", {"file_path": str(self.dir / "grande.tex"), "offset": 1, "limit": 80}))
        self.assertFalse(self.negado("Read", {"file_path": str(self.dir / "pequeno.md")}))

    def test_cat(self):
        self.assertTrue(self.negado("Bash", {"command": "cat grande.tex"}))
        self.assertTrue(self.negado("Bash", {"command": f"cd {self.dir} && cat -n grande.tex"}))
        self.assertFalse(self.negado("Bash", {"command": "cat grande.tex | grep x"}))
        self.assertFalse(self.negado("Bash", {"command": "cat pequeno.md"}))


if __name__ == "__main__":
    unittest.main()
