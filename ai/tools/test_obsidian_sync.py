"""Testes da sincronia comum: python3 tools/test_obsidian_sync.py"""
import pathlib
import tempfile

import obsidian_sync as s


def test():
    with tempfile.TemporaryDirectory() as d:
        v, r = pathlib.Path(d) / "v", pathlib.Path(d) / "r"
        (v / "T").mkdir(parents=True)
        (v / "a.md").write_text("a"); (v / "T" / "b.png").write_bytes(b"\x89")
        (v / "X").mkdir(); (v / "X" / "x.md").write_text("x"); (v / ".obsidian").mkdir()
        (v / ".obsidian" / "w.md").write_text("w")
        s.sincronizar(v, r, excluir={"X"})
        assert (r / "T" / "b.png").exists() and not (r / "X").exists() and not (r / ".obsidian").exists()
        (r / "a.md").write_text("a2"); (v / "T" / "b.png").unlink()
        ac, cf = s.sincronizar(v, r, excluir={"X"})
        assert not cf and len(ac) == 2 and (v / "a.md").read_text() == "a2" and not (r / "T").exists()
        (v / "a.md").write_text("v"); (r / "a.md").write_text("r")
        assert s.sincronizar(v, r) [1] == ["a.md"]
        (r / "a.md").write_text("v")
        # vault sumiu: não apaga o repo; --restaurar recria
        for i in range(8):
            (r / f"n{i}.md").write_text(str(i))
        s.sincronizar(v, r)
        vazio = pathlib.Path(d) / "sumiu"
        try:
            s.sincronizar(vazio, r); assert False
        except s.Abortado:
            pass
        assert len(s.restaurar(vazio, r)) == 10 and (vazio / "n3.md").read_text() == "3"
        # remoção em massa no vault: não replica
        for i in range(8):
            (v / f"n{i}.md").unlink()
        try:
            s.sincronizar(v, r); assert False
        except s.Abortado:
            pass
        assert (r / "n0.md").exists()


if __name__ == "__main__":
    test()
    print("ok    obsidian_sync")
