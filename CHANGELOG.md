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

### Added

- 2026-09-23: The spine folds from its own arrow, not only the split bar. The fold is remembered.
- 2026-09-23: Dev and durable columns can point at any folder. Header click to type, arrow to step up. Saved in `columns.json`.
- 2026-09-23: One selection drives the right side. A folder clicked in a column opens in the companion card, marks its row, and lights its spine tab when it has one. The companion card names its folder and closes with its x.
- 2026-09-23: stratabasor is the main card. The selected repo is its companion card, beside it and offset down. It no longer sits over the dev and durable split. The hover card stacks above the companion.
- 2026-09-23: Branches checked out in another worktree read "local, other worktree". The git `+` mark no longer leaks into the name.
- 2026-09-23: Hover tips on tree rows. Detail scales with the pointer's place across the row, four steps. Shown in the hover card. The far step reads the last commit through `/api/detail`, inside known roots only.
- Local browser, fullscreen, resizable collapsing spine, keybinds file.
- 2026-09-22: A selected directory opens as a card, offset down from the top, over the dev and durable split. The ground split stays. Artifact-scanner is that card on open. The directory, not the scanner app.
- 2026-09-22: Public repository `theRensisioure/stratabasor`.
