# Failure rubric (v1, built from the 163 failure notes)

Each FAILED run gets exactly one primary type: the main reason the hidden tests fail.

| # | Type | Definition | Example from the data |
|---|---|---|---|
| 1 | **Unwired code** | The agent wrote the right kind of new code (helper, model, option) but never connected it to the code path that runs, so behaviour does not change. | truststore: a `_der_bytes()` helper is added but `_verify_peercerts` still calls `.public_bytes()` on bytes |
| 2 | **Missed part of the request** | The issue asks for several things; the agent does some and skips at least one required part (including requested CI tests, test updates or regenerated files). | click: hides hidden commands but not hidden options |
| 3 | **Wrong location** | The change is made in a function or file that is not on the failing code path. | buildozer: `--home-app` added in `build_package()` instead of where the p4a command is built |
| 4 | **Broke existing behaviour** | The change removes or alters behaviour that should be kept (backward compatibility, defaults, edge cases), so other tests break. | qontract: replaces old labels instead of keeping both; `missing_values=None` drops the `['']` default |
| 5 | **Wrong assumption** | The agent believes something false about an API, data shape, value or environment, and builds on it. | Python 3.13 doctest `_stats` values assumed to be 2-tuples (they are 3-tuples); model files `epoch-49` instead of `epoch-99` |
| 6 | **Hidden-test mismatch (underspecified)** | A reasonable solution to the issue as written, but the hidden tests require names, signatures, exact values, payload shapes or files that the issue never states. | clusterscope: tests need `get_mem_per_node_MB`; latex2mathml: tests need exactly `1.623em` |
| 7 | **Looks correct** | The patch appears functionally equivalent to the reference for the issue; the failure is unexplained (possible grader or environment problem). | idempotency key added only for `/session` requests, same as the reference |
| 8 | **Other / unclear** | Not enough evidence to choose, or the note itself is unusable. | — |

Secondary flag (not a type): **over-engineered**, i.e. the agent rewrote far more than needed. It often comes with types 4 and 6.

Notes on using it:
- Types 6 and 7 are not agent mistakes in the usual sense; they point at the task or the grader. Report them separately.
- If two types apply, pick the one that, if fixed, would most likely make the hidden tests pass.
