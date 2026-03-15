# Evals for sketch-to-text

> **Note:** The eval inputs and ground truth files are co-located with the skill for now while the right distribution format for Agent Skill evals is still being worked out. This may move once the pattern is settled.

Each eval case is a single-page PDF paired with a human-reviewed reference output:

- `diagram-N.pdf` — input
- `ground-truth/diagram-N.expected.qmd` — reference output

**The skill must never read `ground-truth/` files during conversion.** Scores are only meaningful if the skill produced its output from the input artifact alone.

## Test cases

| File | Type | Key challenge |
|---|---|---|
| `diagram-1.pdf` | Flowchart with decisions + self-loop | Yes/no branches, return arrow |
| `diagram-2.pdf` | Mixed text + entity sync diagram | Bidirectional arrows, numbered steps |
| `diagram-3.pdf` | Conceptual text + subgraph | Circled actor labels, dashed arrow |
| `diagram-4.pdf` | Data pipeline, cloud shapes | Multiple inputs, cloud output nodes |
| `diagram-5.pdf` | 3-column breakdown structure | Multi-branch from single banner node |
| `diagram-6.pdf` | Side-by-side comparison, two sub-diagrams | Two separate diagrams on one page, diamond shape |
