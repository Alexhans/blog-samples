# Qwen3.5-35B-A3B llama.cpp / pi tuning log

Date: 2026-07-14

Hardware: NVIDIA RTX 4080 Laptop GPU, 12,281 MiB VRAM.

Model: `Qwen3.5-35B-A3B-UD-IQ2_M.gguf`, 10.60 GiB, 34.66B total / 3B active parameters.

llama.cpp: build 9892 (`ee445f93d`).

## llama-bench results

All tests used full GPU offload (`-ngl 99`), flash attention, one repetition, and 64 generated tokens.

| Prompt | K/V cache | Prompt tok/s | Generation tok/s |
|---:|:---:|---:|---:|
| 2,048 | Q8/Q8 | 1,925.70 | 80.39 |
| 2,048 | Q4/Q4 | 1,932.44 | 80.43 |
| 16,384 | Q8/Q8 | 1,994.42 | 81.77 |
| 32,768 | Q8/Q8 | 1,840.30 | 81.94 |
| 49,152 | Q8/Q8 | 1,729.36 | 82.80 |

Initial conclusion: Q8 KV cache fits through 49,152 tokens and has no meaningful generation-speed penalty versus Q4 at short context. Keep Q8 for quality unless real server concurrency or runtime VRAM measurements show insufficient headroom.

## pi baseline settings

- Provider: `llamacpp`
- Model alias: `Qwen3.5-35B-A3B-GGUF`
- Declared context window: 49,152
- Max output: 4,096
- Compaction enabled
- Compaction reserve: 8,192
- Thinking: medium

With a 49,152-token context and 8,192-token reserve, pi should compact at roughly 40,960 occupied tokens (subject to pi's implementation and per-turn output allowance). Real-agent testing is still required.

## First real pi run: 49k/Q8 + 8k reserve

- First turn: 74 seconds, 18 model/tool steps, 32,974 tokens, coherent file-grounded review.
- Continuation reached 47,818 tokens during its tool loop without compaction.
- The following request contained 50,358 tokens and failed against the 49,152 server context.
- Exact error: `400 request (50358 tokens) exceeds the available context size (49152 tokens)`.

Conclusion: pi checks automatic compaction at the outer-turn boundary, but a single tool-heavy turn can grow by roughly 17k tokens. An 8,192 reserve is unsafe for this workload.

## Candidate 2

- Server context: 65,536
- KV: Q4/Q4
- pi reserve: 16,384
- Effective pre-compaction span: about 49,152 tokens
- Loaded VRAM after a request: about 11,622 MiB

This candidate provides enough reserve for the observed long tool turn without reducing the effective working span below the original server's full context.

### Candidate 2 real-agent result

- Compaction triggered once at 50,190 tokens.
- The first post-compaction request was 21,703 tokens.
- The agent retained all five earlier risk findings and completed the requested remediation plan.
- Continuation completed in 64 seconds with no context error.

### 65k/Q8 comparison

65,536 with Q8/Q8 technically loaded, but consumed about 11,942 MiB and left only 56 MiB reported free VRAM during a request. This is too fragile for concurrent desktop/Codex display use. The selected default is therefore **65,536 context, Q4/Q4 KV, 16,384 pi reserve**.

## Recent r/LocalLLaMA findings (2026-07-14 review)

The closest published setup found was an RTX 4070 Super 12 GB running Qwen3.6-35B-A3B-MTP at 128k context. It reported roughly 69–82 generated tok/s across tasks. Important flags included `-fitt 1536`, `-np 1`, flash attention, Q8 KV, context checkpoints, `--no-mmap`, `--mlock`, and MTP speculative decoding. The author emphasized that `-fitt` reserves VRAM and automatically balances GPU/CPU placement; their GPU was not driving a display.

Transferable points:

- Keep meaningful VRAM headroom. A commenter with the same 12,282 MiB capacity reported about 11,800 MiB used as their practical maximum and found `-fitt 512` stable after smaller reserves caused OOMs.
- Test `--no-mmap` versus mmap. One user measured small improvements (~1.5% decode, ~5.2% prompt processing) and lower variance, but other commenters noted higher system-RAM use and workload-dependent results.
- `-np 1` is appropriate for a single-agent workload.
- MTP is the largest prospective generation-speed improvement, especially at long context, but requires Qwen3.6 MTP weights/build support and is not directly applicable to the current Qwen3.5 model.
- Context checkpoints and more aggressive KV formats can extend context further, but quality degradation is not well established in the thread.
- Community reports support testing long-context quality explicitly rather than assuming cache/model quantization is harmless.

Interpretation for this machine:

- The selected 65k/Q4 setup leaves ~376 MiB free, below the 512 MiB stability reserve suggested by the comparable 12 GB report. It passed our workload, but remains an aggressive desktop profile.
- A stability-oriented follow-up should test `-fitt 512` or enough CPU offload to keep at least 512–768 MiB free, plus mmap versus `--no-mmap`.
- A separate performance track should benchmark the already-downloaded Qwen3.6-35B-A3B-MTP GGUF with a compatible MTP configuration. Results should not be mixed with the Qwen3.5 baseline.

## Larger-context correction and benchmarks

The actual objective is to exceed the already-proven 49k setup, not merely stabilize it.

Both larger-context tests used Q4/Q4 KV, flash attention, `-ngl 99`, and `-fitt 768` to reserve VRAM and permit automatic CPU/GPU balancing.

| Allocated context | Filled prompt | Prompt tok/s | Generation tok/s |
|---:|---:|---:|---:|
| 98,304 | 65,536 | 1,081.16 | 67.79 |
| 131,072 | 98,304 | 919.05 | 73.16 |

The 128k benchmark remained stable and showed about 1,588 MiB free VRAM while processing the 98k prompt. The selected experimental profile is therefore:

- Server context: 131,072
- KV cache: Q4/Q4
- Benchmark fit target: 768 MiB
- Real server fit target: 1,536 MiB (768 left only 28 MiB free after server allocation)
- pi reserve: 20,480
- Expected automatic compaction threshold: 110,592 tokens

This yields about 2.25 times the usable span of the original 49,152 context while reserving enough room for the observed ~17k-token tool-heavy turn.

Real-server caveat: the 128k router process reserved nearly all reported VRAM even with `-fitt 1536`, leaving 26 MiB free. Warm API generation measured about 45.2 tok/s. It is retained as a maximum-context profile, not the preferred daily profile.

The preferred daily candidate is 98,304 context, Q4/Q4 KV, `-fitt 512`, and a 16,384 pi reserve. Its expected compaction threshold is 81,920 tokens—exactly twice the original 40,960 threshold from 49,152 context minus the old 8,192 reserve. Real-server warm API generation measured 53.17 tok/s versus 56.66 tok/s on the earlier 49k profile (about 6% lower in these short-request measurements).

## Pi compaction implementation findings

Installed package: `@earendil-works/pi-coding-agent` 0.80.2.

Pi supports three native compaction settings:

- `enabled`
- `reserveTokens`: trigger threshold is `contextWindow - reserveTokens`; it also determines the summarizer output budget, capped by the model's `maxTokens`.
- `keepRecentTokens`: raw recent history retained after compaction; default 20,000.

The default summarizer uses the active model and active thinking level. With this model, summary output is capped at the registered 4,096 `maxTokens`. There is no native settings key for a separate compaction model or thinking level, but the `session_before_compact` extension hook can provide a custom summary.

Selected native setting for the 96k profile: `keepRecentTokens: 24000`. This preserves more recent work verbatim, shortens the summary input modestly, and should leave roughly 58k tokens of new runway after a typical compaction.

The recent `pi-continue` extension is relevant because it guards long tool loops before the next oversized request, supports a separately selected summarizer model/reasoning level/output budget, and resumes the same session from a structured ledger. It must be source-reviewed before installation because Pi extensions execute with the user's permissions.

## pi-continue experiment

Hypothesis: native pi compaction is slow partly because it inherits the agent's medium reasoning and allows up to 4,096 output tokens. `pi-continue` should prevent mid-tool-loop overflow and produce a faster, more durable handoff by using reasoning off and a 2,048-token structured ledger, while leaving normal agent reasoning at medium.

Installed package: `pi-continue` 0.9.3 (no runtime dependencies; npm audit reported no vulnerabilities).

Initial policy:

- Summarizer: `llamacpp/Qwen3.5-35B-A3B-GGUF`
- Summarizer reasoning: off
- History output budget: 2,048 tokens
- Synthesis timeout: 120 seconds
- Mid-run guard: enabled
- Continuation artifacts: disabled
- Agent guide synchronization: disabled
- UI handoff panel: disabled
- Prompt policy: package defaults

Test criteria:

1. No request exceeds the configured context window during a long tool loop.
2. One compaction produces a valid `pi-continue/v4` proof and resumes the same session.
3. Compaction/handoff wall time is lower than native medium-reasoning compaction.
4. The resumed agent retains user constraints, established findings, current work, and the immediate next action.
5. No continuation artifact or AGENTS.md write occurs.

### pi-continue test results: off reasoning / 2,048 output

Source session:

- 48,863 context tokens
- 86 persisted entries
- Source task duration: 153.6 seconds

Harness findings:

- `pi --print "/continue"` does not invoke the extension command; it returned the existing last answer.
- RPC invocation requires stdin to remain open while the asynchronous extension command runs.
- A 60-second RPC harness attempt aborted compaction as the pipe closed. Because shutdown coincided with the failure, this is not counted as a model/JSON failure.
- A warmed repeat with the same policy completed successfully before shutdown.

Successful handoff telemetry:

- Input context: 48,863 tokens
- Estimated post-compaction context reported by the RPC event: 24,407 tokens
- Synthesis request: 12,274 total tokens (7,703 input, 2,771 cache read, 1,800 output)
- Configured/effective output ceiling: 2,048 tokens
- Summary length: 5,383 characters
- Proof: valid `pi-continue/v4`
- Same-session resume request: sent
- Optional continuation artifact: not written
- AGENTS.md: not written

Quality observations:

- Preserved the active task and completion condition.
- Preserved the explicit read-only/no-file-modification constraint.
- Preserved evidence anchors, open verification questions, and ordered next actions.
- Resume began correctly, but re-read some files already represented in the ledger; continuity was safe but not maximally efficient.
- The resumed run was interrupted by the finite RPC harness after two tool calls, so terminal resumed-answer quality is not yet scored.

Current decision: keep `reasoning: off` and `historyMaxTokens: 2048` active. The next decisive test is a natural crossing of the 81,920-token threshold, where the mid-run guard must compact before an oversized request and complete the resumed task without harness shutdown.
