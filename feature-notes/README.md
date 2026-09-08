# Feature notes

Drop new feature ideas here **any time** — after launch, while looking at the live site, whenever one
occurs to you. Freeform: a bullet, a paragraph, a screenshot description, whatever's fastest to jot
down. One file per idea, or a running list — doesn't matter, the workflow below reads whatever's here.

## Workflow

1. **Add a note.** Create/append a file in this folder describing the feature.
2. **Turn notes into tickets.** Run `/to-tickets` on this folder. It reads every note here, creates one
   ticket per feature in `sites/<slug>/.scratch/<slug>/issues/` (numbered from where that tracker left
   off), and moves the consumed note into `done/` so it isn't re-ticketed next time.
3. **Build it.** Run `/implement` (or `/tdd`) on a ticket, same as any other ticket in this site's
   tracker.
4. **Mark it done.** When the ticket's work is finished, set `Status: resolved` in the ticket file —
   same convention as this repo's root issue tracker
   (`docs/agents/issue-tracker.md`). The feature note that spawned it already moved to `done/` in
   step 2; nothing else to file away.

## Folders

- `feature-notes/` (this folder) — new, not-yet-ticketed ideas live directly here.
- `feature-notes/done/` — notes already converted into a ticket. Kept for history, never re-read by
  `/to-tickets`.
