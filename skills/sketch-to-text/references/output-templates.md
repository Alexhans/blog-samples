# Output Templates

## Quarto (.qmd) — default

```yaml
---
title: "{{title from first page or filename}}"
date: "{{YYYY-MM-DD}}"
format:
  html:
    embed-resources: true
---
```

Followed by page sections:

```markdown
## Diagram 1: {{title}}

{{prose if any}}

```{mermaid}
flowchart TD
    ...
```

::: {.callout-caution title="Skill uncertainty notes" collapse="true"}
- "word" — may be "other word"
- Arrow between A and B — direction unclear from sketch
:::
```

Full example:

```
---
title: "Game creation workflow"
date: "2026-03-15"
format:
  html:
    embed-resources: true
---

## Diagram 1: I want to share a game to teach

Flowchart describing the decision process for creating and publishing a game using AI.

```{mermaid}
flowchart TD
    start("I want to share a game to teach")
    describe{"Can I describe the game? Intent"}
    tell_ai("Tell the AI to create game")
    explain("Explain it to the AI and play up scenarios for head")
    iterate["Iterate asking for changes"]
    client_only{"Only client side?"}
    firebase[/Firebase/]
    publish("Publish to easy app")

    start --> describe
    describe -- yes --> tell_ai
    describe -- no --> explain
    explain --> describe
    tell_ai --> iterate
    iterate --> iterate
    iterate --> client_only
    client_only -- yes --> publish
    client_only -- no --> firebase
    firebase --> publish
```

> **Uncertain readings**
> - "play up scenarios for head" — last word may be "ahead" or similar
```

---

## Plain Markdown (.md)

Same structure but:
- No YAML frontmatter (or minimal)
- Use ` ```mermaid ` instead of ` ```{mermaid} `

```markdown
# {{title}}

_Converted from: {{source filename}}_

## Diagram 1: {{title}}

{{prose}}

```mermaid
flowchart TD
    ...
```

> **Uncertain readings**
> - ...
```

---

## Section structure for mixed pages

If a page is mostly text/notes (no diagram):

```markdown
## Page N: {{title or "Notes"}}

{{paragraphs or bullet list}}
```

If a page has both text and a diagram:

```markdown
## Page N: {{title}}

{{prose introduction}}

```{mermaid}
...
```

{{any follow-up text or numbered steps}}
```
