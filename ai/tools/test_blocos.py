import unittest

from np import checar_atributos, checar_blocos, checar_layout


class TestBlocos(unittest.TestCase):
    def test_grudado(self) -> None:
        texto = "def f(x):\n    y = x\n    if y:\n        return 1\n    return 2\n"
        self.assertEqual(checar_blocos(texto), [2, 3, 5])

    def test_separado(self) -> None:
        texto = ("def f(x):\n\n    y = x\n\n    if y:\n        return 1\n\n"
                 "    return 2\n")
        self.assertEqual(checar_blocos(texto), [])

    def test_primeiro_do_bloco_e_comentario(self) -> None:
        # Primeiro comando do if não pede linha; comentário não conta como linha em branco
        texto = ("def f(x):\n\n    if x:\n        return 1\n    # fim\n"
                 "    return 2\n")
        self.assertEqual(checar_blocos(texto), [6])

    def test_def_com_assinatura_longa(self) -> None:
        texto = "def f(\n    x,\n) -> int:\n    return x\n"
        self.assertEqual(checar_blocos(texto), [4])

    def test_simples_seguidos(self) -> None:
        self.assertEqual(checar_blocos("a = 1\nb = 2\nprint(a, b)\n"), [])

    def test_atributo_sem_tipo(self) -> None:
        texto = "class A:\n    x = 1\n    y: int = 2\n"
        self.assertEqual(checar_atributos(texto), [2])

    def test_layout_separado(self) -> None:
        texto = ("# Imports\nimport os\n\n\n# Global variables\nX = 1\nY = 2\n\n\n"
                 "# Code\ndef f():\n\n    return X\n")
        self.assertEqual(checar_layout(texto), [])

    def test_layout_comentario_da_funcao(self) -> None:
        texto = ("# Imports\nimport os\n\n\n# Code\n# O que f faz\ndef f():\n\n"
                 "    return 1\n")
        self.assertEqual(checar_layout(texto), [])

    def test_layout_comentario_da_funcao_sem_titulo(self) -> None:
        texto = "# Imports\nimport os\n\n\n# O que f faz\ndef f():\n\n    return 1\n"
        self.assertEqual(checar_layout(texto), [6])

    def test_layout_uma_linha_so(self) -> None:
        texto = ("# Imports\nimport os\n\n# Global variables\nX = 1\n\n\n"
                 "# Code\ndef f():\n\n    return X\n")
        self.assertEqual(checar_layout(texto), [5])

    def test_layout_globais_separadas(self) -> None:
        texto = "# Global variables\nX = 1\n\nY = 2\n"
        self.assertEqual(checar_layout(texto), [4])

    def test_layout_sem_comentario(self) -> None:
        texto = "# Imports\nimport os\n\n\ndef f():\n\n    return 1\n"
        self.assertEqual(checar_layout(texto), [5])

    def test_layout_global_depois_do_codigo(self) -> None:
        texto = "# Code\ndef f():\n\n    return 1\n\n\nX = 1\n"
        self.assertEqual(checar_layout(texto), [7])


if __name__ == "__main__":
    unittest.main()
