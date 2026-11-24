# test-runner changelog

## 2.0
- Stats files now have a top-level `runner_version` and the per-test records moved under `tests`.
- Each record is now `[tries, failures, skips]`. Note the new order: tries come first.

## 1.4
- Records are `[failures, tries]`.
