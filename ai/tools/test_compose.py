import unittest

from np import servicos_compose


class TestCompose(unittest.TestCase):
    def test_so_os_servicos(self) -> None:
        texto = ("services:\n\n    web:\n        build:\n            context: .\n\n"
                 "    db:\n        image: postgres\n\n\nvolumes:\n    dados:\n")
        self.assertEqual(servicos_compose(texto), ["web", "db"])

    def test_sem_servicos(self) -> None:
        self.assertEqual(servicos_compose("volumes:\n    dados:\n"), [])


if __name__ == "__main__":
    unittest.main()
