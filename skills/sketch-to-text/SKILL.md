---
name: sketch-to-text
description: This skill should be used when the user asks to "convert this PDF to markdown", "convert this image to quarto", "turn my diagram into mermaid", "transcribe my notes", "sketch to text", "scribble to quarto", "turn this sketch into a document", "process my Boox export", or provides a JPEG/PNG/PDF file path and wants it converted to structured text. Converts handwritten notes and diagrams (from Onyx Boox or any source) into Quarto (.qmd) or Markdown with Mermaid diagrams.
version: 0.1.0
---

# sketch-to-text

Convert a handwritten or scanned artifact (JPEG, PNG, PDF) into a structured Quarto document (`.qmd`) or Markdown file with Mermaid diagrams.

## Input

Accept a file path as the primary argument. Optionally accept `--format md` to output plain Markdown with ` ```mermaid ` blocks instead of the default Quarto `.qmd` with `{mermaid}` blocks.

## Workflow

### Step 1: Read the artifact

Use the Read tool on the provided file path. For PDFs with multiple pages, read all pages in a single call (up to 20 pages). Note the total page count.

### Step 2: Classify each page

For each page, identify:

- **Type:** flowchart | sequence diagram | entity/box diagram | mixed text+diagram | notes only | typed text
- **Elements:** title, headings, bullets, labeled nodes, arrows, decision points, free text blocks

### Step 3: Extract structure

For each page:

1. Read the title if present
2. Identify all nodes (shapes: ovals, rectangles, circles, clouds, trapezoids)
3. Identify all edges (arrows, their direction, any labels on them) — **preserve every label written on or beside an arrow**; a labelled arrow must use `-- label -->` not bare `-->`
4. Identify decision points (branches with yes/no or condition labels)
5. Read all free-form text (prose, bullets, numbered lists)
6. Note self-loops and return arrows

### Step 4: Generate output

For each page produce:

- A `## Page N` or titled section header (use the handwritten title if present)
- Any prose/notes as clean Markdown paragraphs or bullet lists
- Any diagram as a Mermaid block (see Diagram Rules below)

Wrap the full output in the appropriate template (see `references/output-templates.md`).

### Step 4b: Self-check the Mermaid

Before writing, review the generated Mermaid syntax:

- Every node ID used in an edge is defined in the node list
- All brackets/parentheses are balanced
- Any label containing `:` is wrapped in `"quotes"`
- Multiline labels use backtick syntax, not bullet characters
- Any `@{ shape: ... }` usage is flagged in the uncertainty callout
- Every arrow that has a label in the sketch uses `-- label -->` — if you wrote a bare `-->` for a labelled arrow, fix it

Fix issues before writing. If the fix is uncertain, output best attempt and note it in the callout block. For renderer-specific issues, direct the user to `references/troubleshooting.md`.

### Step 5: Write the output file

Derive the output filename from the input: same base name, replace extension with `.qmd` (or `.md`). Write the file to the same directory as the input unless the user specifies otherwise.

### Step 6: Report

After writing, summarize:
- Pages processed
- Diagram types found
- Any uncertain readings
- Output file path

## Diagram Rules

### Mermaid diagram type selection

| Page content | Mermaid type |
|---|---|
| Flowchart with decisions (yes/no branches) | `flowchart TD` or `flowchart LR` |
| Steps in sequence between actors | `sequenceDiagram` |
| Nodes with bidirectional sync arrows | `flowchart LR` |
| Concept/entity boxes with relationships | `flowchart TD` |
| Rough mindmap or hierarchy | `mindmap` |

### Node shape mapping

| Handwritten shape | Mermaid syntax | Notes |
|---|---|---|
| Oval / stadium | `node("text")` | Rounded pill |
| Rectangle / box | `node["text"]` | Sharp corners |
| Circle | `node(("text"))` | Circle |
| Double circle / cloud | `node((("text")))` | Terminal, stop, and cloud shapes (outputs, exposures) |
| Diamond / decision | `node{"text"}` | Rhombus |
| Parallelogram | `node[/"text"/]` | Slanted sides |

### Arrow mapping

| Handwritten | Mermaid |
|---|---|
| Single arrow → | `-->` |
| Double-headed ↔ | `<-->` |
| Dashed arrow | `-.->` |
| Labeled arrow | `-- label -->` |

### Multiline node labels

To put multiple lines inside a node, wrap the label in backticks:

```
goals["`Reduce effort
Increase ROI
Fail fast`"]
```

Use this for nodes that contain a list of items in the sketch. Bullet characters are not supported — just newlines.

### Quarto vs plain Markdown fencing

For `--format qmd`:
````
```{mermaid}
flowchart TD
...
```
````

For `--format md`:
````
```mermaid
flowchart TD
...
```
````

## Uncertainty Handling

When a reading is uncertain, never silently guess. Instead:

- Flag inline using an HTML comment: `<!-- uncertain: "word" may be "other word" -->`
- At the end of each page section, append a callout block listing all ambiguities for that page
- For diagram edges where direction is unclear, use `---` (undirected) with a note

For `.qmd` output:
```markdown
::: {.callout-caution title="Skill uncertainty notes" collapse="true"}
- "Anon Blocks" — may be a name abbreviation; exact label unclear
- Arrow between node B and C — direction unclear from sketch
:::
```

For `.md` output:
```markdown
> **[skill]** Uncertainty notes
> - "Anon Blocks" — may be a name abbreviation; exact label unclear
> - Arrow between node B and C — direction unclear from sketch
```

Only include the block if there are actual uncertainties. Omit it on clean pages.

## Multi-page PDFs

For PDFs with multiple pages:

- Create one `## Diagram N` section per page
- Use the handwritten title on each page if present, else `Diagram N`
- Keep all pages in a single output file
- Do not split into separate files unless the user requests it

## Additional Resources

- **`references/output-templates.md`** — QMD frontmatter template, MD template, section structure
- **`references/conversion-guide.md`** — Detailed guidance on reading messy handwriting, inferring intent, handling common Boox OCR failure modes
- **`references/troubleshooting.md`** — Common Mermaid syntax errors, shape compatibility, self-check checklist, and links to Mermaid and Quarto docs
- **`evals/`** — Individual page PDFs used as test inputs

> **Important:** Never read files under `evals/ground-truth/` when processing an input file. Those files are human-reviewed reference outputs used for offline comparison only. Reading them during conversion would contaminate the eval.
