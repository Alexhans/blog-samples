# Find The Loop sample artifacts

These files support the post draft `posts/find-the-loop-story-first.qmd`.

They preserve the measured local LLM configuration loop:

- `benchmark-notes.md`: hypotheses, benchmarks, failures, and decisions.
- `start-llama-server.ps1`: selected PowerShell launcher.
- `models.original.json` / `settings.original.json`: starting `pi` configuration.
- `models.candidate-65k.json` / `settings.candidate-65k.json`: intermediate 65k candidate.
- `models.candidate-96k.json`: candidate `pi` model metadata.
- `settings.candidate-96k.json`: candidate `pi` settings.
- `models.candidate-128k.json` / `settings.candidate-128k.json`: maximum-context candidate.
- `pi-continue.candidate.json`: candidate `pi-continue` policy.

The sample is intentionally the evidence packet, not the full session logs. Raw server logs and `pi` session JSONL files were left out because they are noisy and include unrelated task content from the validation runs.
