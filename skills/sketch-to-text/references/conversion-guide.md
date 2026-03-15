# Conversion Guide

Detailed guidance for converting handwritten Onyx Boox exports to Markdown/Mermaid/Quarto.

## Reading Handwritten Text

### Common Boox handwriting patterns

- Capital letters often look like decorated lowercase (e.g. "I" may look like "l")
- "a" and "o" are frequently confused — use surrounding context to disambiguate
- Arrow labels are often written beside or across the arrow, not on it
- Circled letters like (H) and (A) are node labels or shorthand actors — preserve them as node IDs
- Underlines on text usually mean emphasis, not a heading

### Inferring intent over literal reading

In `interpreted` mode:
- Normalize obvious OCR noise: "teh" → "the", "creat" → "create"
- Expand common abbreviations: "mkt" → "marketing", "cfg" → "config"
- Infer missing articles/prepositions when the meaning is clear
- Do not invent content — only clean clear errors

In `literal` mode:
- Transcribe as-seen, including abbreviations and shorthand
- Flag suspected errors rather than fixing them
- Preserve original capitalization where readable

## Diagram Interpretation

### Flowcharts

Decision nodes are typically:
- Ovals or rounded shapes with a question (or implied question)
- Have multiple outgoing arrows labeled with conditions (yes/no, condition text)
- Sometimes the question mark is written outside the shape

Start/end nodes:
- Ovals or cloud shapes at the top/bottom of the flow
- Often have no incoming or no outgoing arrows respectively

Self-loops (return arrows):
- An arrow that curves back to the same node means "repeat" or "iterate"
- Represent as: `node --> node` with a label like `-- repeat -->`

### Box diagrams (entity/sync)

When boxes have bidirectional arrows with labels like "pull/push" or "sync":
- Use `<-->` for bidirectional
- Or use two separate arrows if the labels differ per direction

When a label appears on an arrow between two nodes:
- Place it as `A -- label --> B`
- If label is long, abbreviate and add a note in the prose

### Sequence diagrams

Use `sequenceDiagram` when:
- There are clearly named actors (columns)
- Arrows go between actors in a time sequence
- Messages/calls are labeled

### Actor shorthand

Circled or labeled actors in the diagram:
- `(H)` = Human
- `(A)` = Agent / AI
- Preserve the shorthand as node IDs but expand in node labels

Example:
```
H(("H (Human)"))
A(("A (Agent)"))
```

## Common Failure Modes

### Ambiguous arrow direction

When you cannot tell which way an arrow points:
- Use `---` (undirected) in Mermaid
- Add a comment: `<!-- uncertain: arrow direction between X and Y -->`

### Overlapping labels

When text is written close to multiple arrows:
- Associate label with the nearest arrow
- If genuinely ambiguous, flag both candidates

### Incomplete content

Pages sometimes have numbered lists that are only partially filled in (e.g., "1. 2." with no content):
- Include the placeholder: `1. *(incomplete)*`
- Do not invent content

### Mixed-language or shorthand

- Preserve proper nouns exactly: Firebase, Obsidian, Google Calendar, Work Outlook
- For product/service names, use the canonical spelling when confident

## Boox-specific Export Characteristics

- Vector PDF exports have clean line strokes — good for diagram structure
- Bitmap PDF/PNG exports have slightly softer edges — still readable
- Lined notebook background (red + gray lines) is visual noise — ignore it
- Handwriting pressure/thickness varies — bold strokes are usually emphasis or titles
- Pages are portrait A5 or letter — content is top-to-bottom, occasionally LR splits for comparisons

## Quality Targets

After conversion, a good output should:
- Render in a Mermaid previewer without syntax errors
- Require ≤5 edits to match the original intent
- Have no silently hallucinated nodes or edges
- Have all uncertain readings explicitly flagged
