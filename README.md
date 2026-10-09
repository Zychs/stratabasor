# stratabasor

Local browser for one job: show a repo the way AyTree's tree tool does. Folders, and the branches on that repo.

The left spine starts empty. The plus has no border and a wide hit area. It opens a field in the window. It does not fullscreen.

The main pane opens as a split: dev on one side, durable on the other. Folders, and branches on any repo in that first level. That split is the main card. A chosen directory opens as its companion card, beside it and offset down from the top.

## Hover

Hold the pointer on a row and the hover card fills in, above the companion card. It keeps the last row until another is hovered. Escape or the x closes it. How far across the row the pointer sits sets how much it says. Four steps, left to right: name and kind; where it sits, its branch, what it holds; full path, size, last change; last commit and what is on disk. The last step asks git only when the pointer gets there.

## Bottle

`/bottle`, from `bottle` at the foot of the spine, reads bottles. A bottle is a folder's `.bottle/bottle.db`, made by `bottle.py snapshot` (journal-clip, `tools/bottle`): every saved version of its .py files. The page finds them in each known root and up to two folders down.

Five levels, each a smaller copy of the one above. Items are the tracked files. Versions are every saved copy. Chapters are a copy's top-level parts: imports, each def and class, module code. Eras are runs of versions in which a chapter's code held still; comments and formatting do not end one. Precious is the chapter's code in an era, against the era before.

Click opens one node and folds the others beside it. Move the pointer out and it folds. Escape folds the deepest.

The module is `bottle/`: `shelf.py` reads, `bottle.html` shows, `test_shelf.py` checks. `serve.py` loads `shelf.py` by path on first use.

```powershell
python -m unittest discover -s C:\dev\stratabasor\bottle
```

## Run

```powershell
python C:\dev\stratabasor\serve.py
```

Opens fullscreen in Edge when Edge is on the machine. Otherwise the same local-browser open AyTree uses. Page is `http://127.0.0.1:8741/`.

## Keys

`keybinds.csv` is the only key list. Each column is a key. Each row is a bind. The column `unbound` is parked. It is not a keyboard key.

`spine.tab.nav` moves the spine tabs. `spine.shortcut` lands on the spine. Both are parked unbound.

## Not

Does not write into `C:\Users\bardw\durable`. Does not create branches. Does not take notes. Does not write into a bottle.
