"""Bottle shelf: read-only access to the .bottle/bottle.db stores under the known roots.

A bottle is a folder's .bottle/bottle.db, written by bottle.py snapshot: one row per
saved version of a .py file (path, sha256, saved_at, source). This module reads them
for the bottle page, bottle.html, and never writes. serve.py loads it by file path.

Five levels, outside in:
    items     tracked .py files
    versions  every saved copy of an item
    chapters  that copy's top-level parts: imports, each def and class, module code
    eras      runs of versions in which a chapter's code held still
    precious  the chapter's code in an era, diffed against the era before

Chapters are cut and compared by the ast, as bottle.py's changelog does, so an edit
to comments or formatting never starts a new era.
"""
from __future__ import annotations

import ast
import difflib
import hashlib
import json
import os
import sqlite3
from contextlib import closing
from functools import lru_cache
from pathlib import Path
from typing import Callable

PAGE = Path(__file__).resolve().parent / "bottle.html"
STORE = Path(".bottle") / "bottle.db"
DEPTH = 2  # look for bottles in each root, its folders, and theirs
SKIP = {"node_modules", "venv", "__pycache__", "obj", "bin"}


def connect(folder: Path) -> sqlite3.Connection:
    """Read-only. A missing store is an error, never created."""
    uri = (Path(folder) / STORE).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=2)


def find(roots: list[str]) -> list[Path]:
    """Folders holding a bottle, at most DEPTH below a root."""
    found: list[Path] = []
    seen: set[str] = set()
    level = [Path(r) for r in roots]
    for depth in range(DEPTH + 1):
        below: list[Path] = []
        for folder in level:
            if (folder / STORE).is_file():
                key = os.path.normcase(str(folder.resolve()))
                if key not in seen:
                    seen.add(key)
                    found.append(folder.resolve())
            if depth == DEPTH:
                continue
            try:
                below += [
                    Path(e.path) for e in os.scandir(folder)
                    if e.is_dir() and not e.name.startswith(".") and e.name not in SKIP
                ]
            except OSError:
                pass
        level = below
    return found


def shelf(roots: list[str]) -> list[dict]:
    """Every bottle under the roots, most recently filled first."""
    out = []
    for folder in find(roots):
        try:
            with closing(connect(folder)) as con:
                items, versions, last = con.execute(
                    "SELECT COUNT(DISTINCT path), COUNT(*), MAX(saved_at) FROM versions"
                ).fetchone()
        except sqlite3.Error:
            continue
        out.append({"root": str(folder), "name": folder.name, "items": items, "versions": versions, "last": last})
    out.sort(key=lambda b: b["last"] or "", reverse=True)
    return out


def items(folder: Path) -> list[dict]:
    with closing(connect(folder)) as con:
        rows = con.execute("SELECT path, COUNT(*), MAX(saved_at) FROM versions GROUP BY path").fetchall()
    return [{"path": p, "versions": n, "last": last} for p, n, last in rows]


def chapters(source: str) -> dict[str, dict] | None:
    """Top-level parts in source order, keyed "imports", "def f", "class C", or "module".

    Like bottle.py's structure(): imports share one chapter, as does the rest of the
    module-level code, and a later def of the same name replaces the earlier one.
    Comment lines directly above a statement travel with it. None when it won't parse.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: dict[str, dict] = {}
    floor = 0  # last line of the statement before, so comments are never taken twice
    for node in tree.body:
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        while start - 1 > floor and lines[start - 2].startswith("#"):
            start -= 1
        text = "\n".join(lines[start - 1:node.end_lineno])
        doc = None
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            key, kind, name = "imports", "imports", "imports"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            key, kind, name, doc = f"def {node.name}", "def", node.name, ast.get_docstring(node)
        elif isinstance(node, ast.ClassDef):
            key, kind, name, doc = f"class {node.name}", "class", node.name, ast.get_docstring(node)
        else:
            key, kind, name, doc = "module", "module", "module code", ast.get_docstring(tree)
        part = out.get(key)
        if part and kind in ("imports", "module"):
            part["text"] += ("\n" if start == part["end"] + 1 else "\n\n") + text
            part["shape"] += "\n" + ast.dump(node)
            part["end"] = node.end_lineno
        else:
            out[key] = {"kind": kind, "name": name, "text": text, "shape": ast.dump(node),
                        "end": node.end_lineno, "line": start, "doc": first_line(doc)}
        floor = node.end_lineno
    return out


def first_line(doc: str | None) -> str | None:
    """A docstring's first line: the chapter's epigraph on the bottle page's book card."""
    line = doc.strip().split("\n")[0].strip() if doc else ""
    return line[:160] or None


def whole(source: str) -> dict[str, dict]:
    """A version that won't parse is one chapter: the whole file."""
    text = source.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return {"unparsed": {"kind": "unparsed", "name": "whole file", "text": text, "line": 1, "doc": None,
                         "shape": hashlib.sha256(source.encode("utf-8")).hexdigest()}}


def rows(before: list[str] | None, now: list[str]) -> list[list[str]]:
    """[op, line] pairs: "=" kept, "-" gone since the era before, "+" new in this one."""
    if before is None:
        return [["=", line] for line in now]
    out: list[list[str]] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, before, now, autojunk=False).get_opcodes():
        if op == "equal":
            out += [["=", line] for line in now[j1:j2]]
            continue
        out += [["-", line] for line in before[i1:i2]]
        out += [["+", line] for line in now[j1:j2]]
    return out


def item(folder: Path, path: str) -> dict | None:
    """One item, every level below it. Cached until the store changes."""
    store = (Path(folder) / STORE).resolve()
    st = store.stat()
    return _item(str(Path(folder).resolve()), st.st_mtime_ns, st.st_size, path)


@lru_cache(maxsize=16)
def _item(folder: str, mtime: int, size: int, path: str) -> dict | None:
    with closing(connect(Path(folder))) as con:
        saved = con.execute(
            "SELECT saved_at, sha256, source FROM versions WHERE path = ? ORDER BY id", (path,)
        ).fetchall()
    if not saved:
        return None
    versions: list[dict] = []
    eras: dict[str, list[dict]] = {}
    live: dict[str, dict] = {}  # each present chapter's current era
    prev = None
    for n, (at, sha, source) in enumerate(saved, start=1):
        cut = chapters(source)
        parsed = cut is not None
        cut = cut if parsed else whole(source)
        for key, part in cut.items():
            era = live.get(key)
            if era and era["shape"] == part["shape"]:
                era["to"], era["text"] = n, part["text"]
            else:
                eras.setdefault(key, []).append({"from": n, "to": n, "shape": part["shape"], "text": part["text"]})
        live = {key: eras[key][-1] for key in cut}

        status: dict[str, str] = {}
        removed: list[dict] = []
        delta = None
        if prev is not None:
            if not parsed or not prev["parsed"]:
                delta = {"unparsed": True}
            else:
                old = prev["cut"]
                for key, part in cut.items():
                    if key not in old:
                        status[key] = "new"
                    elif old[key]["shape"] != part["shape"]:
                        status[key] = "changed"
                removed = [face(key, old[key], "removed") for key in old if key not in cut]
                delta = {
                    "add": sum(s == "new" for s in status.values()),
                    "chg": sum(s == "changed" for s in status.values()),
                    "del": len(removed),
                }
        versions.append({
            "n": n, "at": at, "sha": sha, "lines": len(source.splitlines()), "parsed": parsed, "delta": delta,
            "chapters": [face(key, part, status.get(key)) for key, part in cut.items()] + removed,
        })
        prev = {"cut": cut, "parsed": parsed}

    for runs in eras.values():
        before = None
        for era in runs:
            now = era.pop("text").split("\n")
            del era["shape"]
            era["rows"] = rows(before, now)
            before = now
    return {"path": path, "versions": versions, "eras": eras}


def face(key: str, part: dict, status: str | None) -> dict:
    return {"key": key, "kind": part["kind"], "name": part["name"], "line": part["line"],
            "lines": part["text"].count("\n") + 1, "doc": part["doc"], "status": status}


def _json(code: int, body: object) -> tuple[int, str, bytes]:
    return code, "application/json; charset=utf-8", json.dumps(body).encode("utf-8")


def route(path: str, qs: dict, roots: list[str], allow: Callable[[str], str | None]) -> tuple[int, str, bytes]:
    """GET /bottle and /api/bottle/*. Returns (status, content type, body).

    allow() resolves a path when it sits inside a known root, else None. Only
    bottles inside known roots are read.
    """
    if path == "/bottle":
        return 200, "text/html; charset=utf-8", PAGE.read_bytes()
    if path == "/api/bottle/shelf":
        return _json(200, {"bottles": shelf(roots)})
    folder = allow((qs.get("root") or [""])[0])
    if not folder or not (Path(folder) / STORE).is_file():
        return _json(404, {"error": "missing"})
    try:
        if path == "/api/bottle/items":
            return _json(200, {"root": folder, "items": items(Path(folder))})
        if path == "/api/bottle/item":
            found = item(Path(folder), (qs.get("path") or [""])[0])
            return _json(200, found) if found else _json(404, {"error": "missing"})
    except sqlite3.Error as e:
        return _json(500, {"error": str(e)})
    return _json(404, {"error": "missing"})
