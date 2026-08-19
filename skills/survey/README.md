# survey

An Agent Skill for authoring and answering lightweight surveys where **every
answer can carry a free-text note**, and where **Skip** and **I don't know** are
first-class answers.

## Prototype Status

**This is an anonymized illustration, not a working skill.** It accompanies the
blog post [Add a Skip and a Note to Every Question](https://alexhans.github.io/posts/add-a-skip-and-a-note.html).

- Goal: show the *shape* of a skill built around the "note on every answer" idea.
- Anonymized: internal tool names, storage paths, and destinations were replaced
  with generic placeholders (`~/surveys/`, `~/.config/survey/`, `The assistant`,
  `Legacy dashboard`, `johndoe`/`janedoe`).
- Not wired to anything: it references generic Slack tool names (`post_message`,
  `lookup_user`, …) but is not connected to a real workspace or install.
- Tradeoffs: no code, no tests, no packaging; it is a `SKILL.md` and this README.
- Next step: fork and adapt the *ideas*, not this file.

## Why This Matters

The point of the skill is one design decision: a survey answer travels with its
reason. A multiple-choice pick is a number; the note beside it is what you can act
on. The skill also makes non-answers honest: an easy Skip beats a fatigued
respondent picking anything, and beats a dropped survey. The blog post explains
the reasoning; this file shows how it looks encoded as agent instructions.

## What You Can Change

- The **question format** convention (how titles, questions, and options parse).
- The **respond flow**: how each question is asked and how Skip / I don't know /
  note are offered.
- The **destination and storage**: where results go and whether a local copy is
  kept.

## Notes

- Known limitations: not runnable as-is; Slack tool names are illustrative.
- The richest version of this depends on an **agent being the medium** for
  answering (it can reinterpret a question and draw the respondent out). A plain
  form can't do that; see the post's "Coding Agents" section.

## Ideas For Next Iteration

1. Aggregate saved JSON responses into a year-over-year view with note excerpts.
2. Detect near-duplicate options at authoring time and suggest merges.
3. Summarize free-text notes per question with an LLM once responses are in.
