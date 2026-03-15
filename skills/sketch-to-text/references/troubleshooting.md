# Troubleshooting

## Reference docs

- **Mermaid flowchart syntax:** https://mermaid.js.org/syntax/flowchart.html
- **Mermaid new shapes:** https://mermaid.js.org/syntax/flowchart.html#complete-list-of-new-shapes
- **Quarto diagrams (Mermaid + Graphviz):** https://quarto.org/docs/authoring/diagrams.html#mermaid
- **Live Mermaid renderer:** https://mermaid.live

## Common errors

### "Syntax error in text"

Generic Mermaid parse error. Most common causes:

- Unbalanced brackets or parentheses in a node definition
- A colon `:` inside a label without quotes — e.g. `node[exposure: Dashboard]` fails; use `node["exposure: Dashboard"]`
- A node ID referenced in an edge that was never defined
- `@{ shape: ... }` used with an older Mermaid version (requires v11.3.0+)
- Mixing `@{ shape: X, label: "..." }` and `["label"]@{ shape: X }` — pick one form; `["label"]@{ shape: X }` is the safer pattern

### Shape not rendering / falling back to rectangle

- `@{ shape: cloud }` — not implemented in Quarto's bundled Mermaid renderer; use `((("text")))` (double circle) instead
- Check Quarto's bundled Mermaid version: run `quarto check` and look for the Mermaid version line
- Test shapes in isolation at https://mermaid.live before committing to a file

### Multiline labels not working

- Requires backtick syntax: `` node["`line1\nline2`"] ``
- Bullet characters (`-`, `*`) inside node labels are not supported — use plain newlines only

### Self-loop renders in unexpected position

- Mermaid uses Dagre for auto-layout; self-loops like `A --> A` will be placed at Dagre's discretion
- No workaround in standard flowchart syntax — accept the layout or restructure the diagram

### Edge label not showing

- Label must be between `--` markers: `A -- label --> B` or `A -->|label| B`
- Spaces around the label are required in the `-- label -->` form

## Self-check before outputting

Before writing the output file, review the generated Mermaid for:

1. Every node ID used in an edge is defined in the node list
2. All brackets/parentheses are balanced (`[`, `(`, `((`, `(((` each closed)
3. Any label containing `:` is wrapped in `"quotes"`
4. `@{ shape: ... }` shapes are flagged in the uncertainty notes if renderer compatibility is unknown
5. Multiline labels use backtick syntax, not bullet characters

If any issue is found, fix it before writing. If the correct fix is uncertain, output the best attempt and note the issue in the callout block.
