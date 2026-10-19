"""Testes do lint de commit: python3 -m unittest tools/test_commit_msg.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commit_msg import erros  # noqa: E402


class TestCommitMsg(unittest.TestCase):
    def test_validas(self):
        for msg in ("Add headings to codemirror editor",
                    "Create headings decoration\n\nThe parser marks ATX headings only.",
                    "Merge branch 'add-sync' into master",
                    'Revert "Add headings to codemirror editor"',
                    "fixup! Add headings to codemirror editor"):
            self.assertEqual(erros(msg), [], msg)

    def test_invalidas(self):
        casos = {
            "wip": "não diz",
            "wip 2": "não diz",
            "feat: Add sync": "prefixo",
            "add sync": "maiúscula",
            "Add sync.": "ponto final",
            "Added sync": "imperativo",
            "Adiciona sincronização": "inglês",
            "Add sync\nbody": "linha em branco",
            "Add sync\n\nCo-Authored-By: Claude <x@y>": "Claude",
            "A" * 73: "72",
        }
        for msg, trecho in casos.items():
            self.assertTrue(any(trecho in e for e in erros(msg)), f"{msg!r}: {erros(msg)}")


if __name__ == "__main__":
    unittest.main()
