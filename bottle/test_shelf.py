"""Tests for the bottle shelf. Run: python -m unittest discover -s bottle"""
import hashlib
import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shelf = load("stratabasor_shelf", HERE / "shelf.py")


def fill(folder, rows):
    """Write (path, saved_at, source) rows into the same table bottle.py snapshot does."""
    store = Path(folder) / ".bottle" / "bottle.db"
    store.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(store)
    con.execute(
        "CREATE TABLE IF NOT EXISTS versions (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, "
        "sha256 TEXT NOT NULL, saved_at TEXT NOT NULL, source TEXT NOT NULL)"
    )
    con.executemany(
        "INSERT INTO versions (path, sha256, saved_at, source) VALUES (?, ?, ?, ?)",
        [(p, hashlib.sha256(s.encode("utf-8")).hexdigest(), at, s) for p, at, s in rows],
    )
    con.commit()
    con.close()


def allow_under(*roots):
    def allow(path):
        resolved = Path(path).resolve()
        ok = any(resolved == Path(r).resolve() or Path(r).resolve() in resolved.parents for r in roots)
        return str(resolved) if path and ok else None
    return allow


SOURCE = '''#!/usr/bin/env python3
"""Doc."""
import os

TEMPLATE = """
def fake():
    pass
"""


# keeps rows
@staticmethod
def helper(x):
    return x


class Store:
    def add(self, row):
        pass


import sys


async def serve():
    return 1


def helper(x):
    return x * 2


if __name__ == "__main__":
    serve()
'''


class ChaptersTest(unittest.TestCase):
    def test_cut_like_bottle(self):
        cut = shelf.chapters(SOURCE)
        self.assertEqual(list(cut), ["module", "imports", "def helper", "class Store", "def serve"])
        self.assertEqual(cut["imports"]["text"], "import os\n\nimport sys")
        self.assertIn("def fake():", cut["module"]["text"], "a def inside a string is module code")
        self.assertNotIn("def fake", cut)
        self.assertEqual(cut["def helper"]["text"], "def helper(x):\n    return x * 2", "the later def wins")
        self.assertEqual(cut["def serve"]["kind"], "def")

    def test_comments_and_decorators_travel_with_the_def(self):
        cut = shelf.chapters("x = 1\n\n# keeps rows\n@dec\ndef f():\n    pass\n")
        self.assertEqual(cut["def f"]["text"], "# keeps rows\n@dec\ndef f():\n    pass")

    def test_chapters_carry_their_first_line_and_docstring(self):
        cut = shelf.chapters('"""Module.\n\nMore."""\nimport os\n\n\n# note\ndef f():\n    """Does f.\n\n    Long."""\n')
        self.assertEqual((cut["module"]["line"], cut["module"]["doc"]), (1, "Module."))
        self.assertEqual((cut["imports"]["line"], cut["imports"]["doc"]), (4, None))
        self.assertEqual((cut["def f"]["line"], cut["def f"]["doc"]), (7, "Does f."), "line counts the comment above")

    def test_unparsable_is_none(self):
        self.assertIsNone(shelf.chapters("def (:\n"))


class ItemTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def item(self, *sources):
        fill(self.root, [("m.py", f"2026-10-0{i}T00:00:00+00:00", s) for i, s in enumerate(sources, start=1)])
        return shelf.item(self.root, "m.py")

    def test_comment_and_spacing_edits_keep_the_era(self):
        it = self.item("def a():\n    return 1+1\n", "def a():\n    # two\n    return 1 + 1\n")
        self.assertEqual([(e["from"], e["to"]) for e in it["eras"]["def a"]], [(1, 2)])
        self.assertEqual(it["versions"][1]["delta"], {"add": 0, "chg": 0, "del": 0})

    def test_changes_and_gaps_start_new_eras(self):
        it = self.item(
            "def a():\n    return 1\n",
            "def a():\n    return 2\n",
            "def b():\n    pass\n",
            "def a():\n    return 2\n\n\ndef b():\n    pass\n",
        )
        self.assertEqual([(e["from"], e["to"]) for e in it["eras"]["def a"]], [(1, 1), (2, 2), (4, 4)])
        self.assertEqual(it["eras"]["def a"][1]["rows"], [["=", "def a():"], ["-", "    return 1"], ["+", "    return 2"]])
        v2, v3 = it["versions"][1], it["versions"][2]
        self.assertEqual([(c["key"], c["status"]) for c in v2["chapters"]], [("def a", "changed")])
        self.assertEqual([(c["key"], c["status"]) for c in v3["chapters"]], [("def b", "new"), ("def a", "removed")])
        self.assertEqual(v3["delta"], {"add": 1, "chg": 0, "del": 1})

    def test_a_version_that_will_not_parse_is_one_whole_chapter(self):
        it = self.item("x = 1\n", "def (:\n", "x = 2\n")
        v2, v3 = it["versions"][1], it["versions"][2]
        self.assertFalse(v2["parsed"])
        self.assertEqual([c["key"] for c in v2["chapters"]], ["unparsed"])
        self.assertEqual(v2["delta"], {"unparsed": True})
        self.assertEqual(v3["delta"], {"unparsed": True})
        self.assertEqual(it["eras"]["unparsed"][0]["rows"], [["=", "def (:"]])

    def test_unknown_item_is_none(self):
        self.item("x = 1\n")
        self.assertIsNone(shelf.item(self.root, "nope.py"))


class ShelfTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        for folder in ("a", "b/c", "d/e/f", ".hidden/x"):
            fill(self.root / folder, [("m.py", "2026-10-01T00:00:00+00:00", "x = 1\n")])

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_bottles_up_to_two_folders_down(self):
        names = sorted(Path(b["root"]).relative_to(self.root).as_posix() for b in shelf.shelf([str(self.root)]))
        self.assertEqual(names, ["a", "b/c"])

    def test_reads_only_inside_known_roots(self):
        inside = self.root / "a"
        allow = allow_under(inside)
        code, _, _ = shelf.route("/api/bottle/items", {"root": [str(self.root / "b" / "c")]}, [str(inside)], allow)
        self.assertEqual(code, 404)
        code, kind, body = shelf.route("/api/bottle/items", {"root": [str(inside)]}, [str(inside)], allow)
        self.assertEqual((code, kind.split(";")[0]), (200, "application/json"))
        self.assertIn(b'"m.py"', body)

    def test_reading_writes_nothing(self):
        folder = self.root / "a"
        store = folder / ".bottle" / "bottle.db"
        before = (store.read_bytes(), sorted(os.listdir(store.parent)))
        allow = allow_under(self.root)
        for path, qs in (("/api/bottle/shelf", {}), ("/api/bottle/items", {"root": [str(folder)]}),
                         ("/api/bottle/item", {"root": [str(folder)], "path": ["m.py"]})):
            self.assertEqual(shelf.route(path, qs, [str(self.root)], allow)[0], 200, path)
        self.assertEqual((store.read_bytes(), sorted(os.listdir(store.parent))), before)

    def test_serve_loads_the_module_by_path_and_serves_the_page(self):
        serve = load("stratabasor_serve_under_test", HERE.parent / "serve.py")
        code, kind, body = serve.bottle_shelf().route("/bottle", {}, [], allow_under())
        self.assertEqual((code, kind.split(";")[0]), (200, "text/html"))
        self.assertIn(b"precious", body)


if __name__ == "__main__":
    unittest.main()
