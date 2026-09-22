# stratabasor

Local browser for one job: show a repo the way AyTree's tree tool does. Folders, and the branches on that repo.

The left spine starts empty. The plus has no border and a wide hit area. It opens a field in the window. It does not fullscreen.

The main pane opens as a split: dev on one side, durable on the other. Folders, and branches on any repo in that first level. A chosen directory opens as a card over that split, offset down from the top.

## Run

```powershell
python C:\dev\stratabasor\serve.py
```

Opens fullscreen in Edge when Edge is on the machine. Otherwise the same local-browser open AyTree uses. Page is `http://127.0.0.1:8741/`.

## Keys

`keybinds.csv` is the only key list. Each column is a key. Each row is a bind. The column `unbound` is parked. It is not a keyboard key.

`spine.tab.nav` moves the spine tabs. `spine.shortcut` lands on the spine. Both are parked unbound.

## Not

Does not write into `C:\Users\bardw\durable`. Does not create branches. Does not take notes.
