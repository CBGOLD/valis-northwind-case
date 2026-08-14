# LLM logs

AI-native build, disclosed end-to-end. Layout:

- `prompts/` — the exact prompts, verbatim, as given to each model run.
- `runs/` — one record per model run: metadata JSON (model, role, timing, tool-use counts) plus the
  run's verbatim output where the run produced a standalone deliverable (`.md` next to the `.json`).

Two roles were used deliberately (gauntlet pattern): **Fable** builds in the main loop;
**Opus** ran once, fresh-context and read-only, to establish ground truth *independently before
seeing any builder output* — its findings were then reconciled against the build (see
`BUILD_LOG.md`, 2026-08-15 00:0x entries). The harness does not expose raw API transcripts;
these records are the faithful structured equivalent, written at build time, not reconstructed.
