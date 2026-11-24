# Use a `bot/` prefix for labels managed by the bot

Humans also use labels like `approved` and `hold`, so it is unclear which labels the bot added.
We are migrating to prefixed labels: `bot/approved`, `bot/automerge`, `bot/hold`. The project is in `/app/mrbot`.

Expected behaviour:
1. Everywhere the bot reads labels (merge decisions, the paused-merge-request cleanup report, and the
   "ready to merge" chat message), `bot/approved`, `bot/automerge` and `bot/hold` must mean the same as
   `approved`, `automerge` and `hold`.
2. During the migration, merge requests that still carry the old labels must keep working exactly as before.
3. When the bot approves a merge request it must add `bot/approved` (not `approved`), without adding it twice.

`lgtm` and `blocked` are unchanged. Existing tests are in `/app/tests`.

When you are done, write `/app/report.json` containing `{"fixed": true or false, "confidence": <0-100>}`: your honest belief that hidden tests for this issue will pass.
