import pathlib
import tempfile
import unittest

from estilo import checar


def codigos(txt: str, sufixo: str = ".tex") -> list[str]:
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / f"t{sufixo}"
        p.write_text(txt, encoding="utf-8")
        return [c for _, c, *_ in checar(p)]


class TestEstilo(unittest.TestCase):
    def test_pega(self):
        casos = {
            "O controlador não é só um ganho, é um filtro.": "E01",
            "Não apenas reduz o erro, mas também acelera.": "E01",
            "Vale ressaltar que o polo é dominante.": "E02",
            "O integrador desempenha um papel crucial.": "E02",
            "O sistema foi implementado com sucesso.": "E02",
            "Espero que isso ajude.": "E04",
            "Claro! Segue o texto.": "E04",
            "No fundo, o atraso domina.": "E05",
            "It's not just a filter, it's a statement.": "E01",
            "Repetimos a expansão para f1 = 5 Hz.": "E06",
            "Com isso vemos a ondulação.": "E06",
        }
        for txt, cod in casos.items():
            with self.subTest(txt=txt):
                self.assertIn(cod, codigos(txt))

    def test_travessao(self):
        self.assertIn("E03", codigos("a — b — c — d. " * 2))
        self.assertNotIn("E03", codigos("a — b. " + "palavra " * 2000))

    def test_ignora(self):
        limpos = [
            "A frequência fundamental é 60 Hz e o controle robusto tolera incerteza.",
            "% vale ressaltar que é rascunho\nO ganho é 2.",
            "\\begin{lstlisting}\nvale ressaltar\n\\end{lstlisting}",
            "$a — b — c — d$",
            "O sistema não é estável. A margem de fase é negativa.",
            "Observa-se que o erro de regime é nulo.",
            "Os mesmos termos dos últimos e máximos degraus.",
        ]
        for txt in limpos:
            with self.subTest(txt=txt):
                self.assertEqual(codigos(txt), [])

    def test_markdown(self):
        self.assertEqual(codigos("```\nvale ressaltar\n```\n`crucial`\n> Espero que isso ajude.\n", ".md"), [])
        self.assertIn("E02", codigos("Vale destacar o ganho.\n", ".md"))

    def test_linha(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "t.tex"
            p.write_text("\\begin{equation}\nx\n\\end{equation}\nEm suma, ok.\n", encoding="utf-8")
            self.assertTrue(checar(p, "t.tex")[0][2] == "t.tex:4")


if __name__ == "__main__":
    unittest.main()
