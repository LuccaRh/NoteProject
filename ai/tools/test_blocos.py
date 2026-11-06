import unittest

from np import (
    checar_atributos,
    checar_blocos,
    checar_docstrings,
    checar_camadas,
    checar_comentarios,
    checar_constantes,
    checar_layout,
    checar_parametros,
    checar_posicionais,
    checar_prompts,
)


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


    def test_constante_importada(self) -> None:
        texto = "from lonzo.a import MODEL, get\nfrom os import SEEK_SET\nfrom lonzo.b import f\n"
        self.assertEqual(checar_constantes(texto, "lonzo"), [1])

    def test_chamada_posicional(self) -> None:
        texto = ("def f(a, b):\n    return a\n\n\nf(1, b=2)\nf(a=1, b=2)\nprint(1)\n"
                 "class C:\n    def g(self, x):\n        self.g(1)\n        x.g(1)\n")
        self.assertEqual(checar_posicionais(texto, {"f", "g"}), [5, 10])


if __name__ == "__main__":
    unittest.main()


class TestParametros(unittest.TestCase):
    def test_um_por_linha(self) -> None:
        texto = "def f(\n    a: int,\n    b: int,\n) -> int:\n    return g(\n        x=a,\n        y=b,\n    )\n"
        self.assertEqual(checar_parametros(texto), [])

    def test_pendurados(self) -> None:
        texto = "def f(\n    a: int, b: int\n) -> int:\n    return g(\n        x=a, y=b\n    )\n"
        self.assertEqual(checar_parametros(texto), [1, 4])

    def test_primeiro_na_linha_do_parentese(self) -> None:
        self.assertEqual(checar_parametros("g(a,\n  b)\n"), [1])

    def test_um_so_abraca(self) -> None:
        self.assertEqual(checar_parametros("g(h(\n    x=1,\n    y=2,\n))\n"), [])


class TestDocstrings(unittest.TestCase):
    def test_com_docstring(self) -> None:
        texto = 'def f() -> None:\n    """\n    Faz algo\n    """\n\n    return\n'
        self.assertEqual(checar_docstrings(texto), [])
        self.assertEqual(checar_blocos(texto), [])

    def test_docstring_separada_da_assinatura(self) -> None:
        texto = 'def f() -> None:\n\n    """\n    Faz algo\n    """\n\n    return\n'
        self.assertEqual(checar_blocos(texto), [3])

    def test_codigo_grudado_na_docstring(self) -> None:
        texto = 'class A:\n    """\n    Algo\n    """\n    x: int\n'
        self.assertEqual(checar_blocos(texto), [5])

    def test_comentario_em_cima(self) -> None:
        texto = "# Faz algo\ndef f() -> None:\n    return\n\nclass A:\n    x: int\n"
        self.assertEqual(checar_docstrings(texto), [2, 5])


class TestCamadas(unittest.TestCase):
    def test_router_com_service(self) -> None:
        texto = "from lonzo.services.chat import answer\n"
        self.assertEqual(checar_camadas(texto, "lonzo"), [])

    def test_router_com_client_ou_conexao(self) -> None:
        texto = (
            "from lonzo.clients.ichiro import IchiroClient\n"
            "from lonzo.connections import ichiro\n"
            "from lonzo import connections\n"
            "from fastapi import APIRouter\n"
        )
        self.assertEqual(checar_camadas(texto, "lonzo"), [1, 2, 3])

    def test_router_com_repository(self) -> None:
        texto = "from ichiro.repositories.notes import select_note\n"
        self.assertEqual(checar_camadas(texto, "ichiro"), [1])

    def test_router_com_conexao_do_banco(self) -> None:
        texto = "from ichiro.db import get_conn\nfrom ichiro import db\n"
        self.assertEqual(checar_camadas(texto, "ichiro"), [1, 2])

    def test_comentario_de_uma_linha(self) -> None:
        texto = "# Code\n# Fake stream\nx = 1  # a\n# b\ny = 2\n"
        self.assertEqual(checar_comentarios(texto), [])

    def test_comentario_de_duas_linhas(self) -> None:
        texto = "def f():\n    # first\n    # second\n    return 1\n"
        self.assertEqual(checar_comentarios(texto), [3])

    def test_colunas_em_global_nao_e_prompt(self) -> None:
        texto = 'COLUMNS = "api_key, key_end, model, a, b, c, d, show_workspace"\n'
        self.assertEqual(checar_prompts(texto), [])

    def test_prompt_em_global(self) -> None:
        texto = (
            '# Global variables\nHINT = (\n    "Search the folder first and then"\n'
            '    " every note before saying no."\n)\n'
        )
        self.assertEqual(checar_prompts(texto), [2])

    def test_global_curta_nao_e_prompt(self) -> None:
        texto = (
            'URL = "http://ichiro:8000"\nFOLDERS = ["kb", "skills"]\n'
            'def f():\n    x = "a long error message with many words in it"\n'
        )
        self.assertEqual(checar_prompts(texto), [])
