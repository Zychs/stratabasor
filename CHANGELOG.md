# Changelog

Reverse-chronological. Dates are local. No version scheme. Stay on Unreleased.

## [Unreleased]

### LOCKED

- 2026-09-22: The reading pane is folders plus branches, the AyTree tree-tool part. Not the workbench list that skips branches.
- 2026-09-22: Spine starts empty. One plus. Field stays in the window.
- 2026-09-22: `spine.tab.nav` and `spine.shortcut` stay parked on the `unbound` column until a real key column is filled.
- 2026-09-22: Read-only. No branch creation. No writes into the durable haven.

### PARKED

- The second Vision corpse. One corpse is named. Do not guess the other.

### Changed

- 2026-10-09: Bottle page trimmed. No ornament: no serif, numerals, fleuron, ribbon, glow, or animation. Denser rows, and brightness carries importance: changed chapters, the era holding the version, and the lines an era brought read bright; the rest steps back. A fold no longer slides content under the pointer at the top of the page.
- 2026-09-25: Merged the hover card from upstream. The selected directory stays the third column; the dock beside the tree now holds only the hover card, themed from the background pick.

- 2026-09-24: The selected directory is a third column beside dev and durable, not a card over them. It changes whenever a folder, repo, or branch group is picked. A file pick leaves it alone.
- 2026-09-24: The overlay card is now the background picker, opened from `colors` at the foot of the spine. Blue and its complement, each varying only in brightness. Text and line tones are derived from the pick; a swatch is only offered when body text clears 7:1 on every surface it sits on.
- 2026-09-24: Rows carry a type tone: repo, folder, hidden folder, branches, head, local, remote, and files sorted into code, doc, data, config, media. The tone is an edge bar and a chip behind the kind label. Profiles (Kinds, Files, Repos, Off) in the color overlay decide which types get which tone. Chip labels clear 7:1 against their own chip.

### Added

- 2026-10-09: Book card beside the bottle fractal, in house negentropic-blue (journal-clip `clip_look.py`). The attended version reads as a contents page, the attended chapter as a book chapter, its docstring the epigraph. Attention is window focus × mouse coherence; it turns the card's page after a short rest and sets its order: frame, text focus, ribbon.
- 2026-10-09: Bottle page at `/bottle`, from `bottle` at the foot of the spine. Browses the `.bottle/bottle.db` stores under the known roots as a fractal: items, versions, chapters, eras, precious. Click opens one node; moving the pointer out folds it. Read-only. Self-contained in `bottle/`; `serve.py` loads it by path. The page wears the tint picked in `colors`.
- 2026-09-23: stratabasor is the main card. The selected repo is its companion card, beside it and offset down. It no longer sits over the dev and durable split. The hover card stacks above the companion.
- 2026-09-23: Branches checked out in another worktree read "local, other worktree". The git `+` mark no longer leaks into the name.
- 2026-09-23: Hover tips on tree rows. Detail scales with the pointer's place across the row, four steps. Shown in the hover card. The far step reads the last commit through `/api/detail`, inside known roots only.
- Local browser, fullscreen, resizable collapsing spine, keybinds file.
- 2026-09-22: A selected directory opens as a card, offset down from the top, over the dev and durable split. The ground split stays. Artifact-scanner is that card on open. The directory, not the scanner app.
- 2026-09-22: Public repository `theRensisioure/stratabasor`.
