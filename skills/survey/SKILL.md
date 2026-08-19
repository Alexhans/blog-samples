---
name: survey
description: Create a lightweight survey as a plain Slack message and answer surveys others share. Every question lets the respondent add a free-text note, skip, or say "I don't know", so answers always carry context. Use when the user says "make a survey", "create a poll", "answer this survey", "run this survey", or pastes a survey message/link and wants to respond.
tags: [skill, survey, poll, slack, feedback]
---

<!--
ANONYMIZED EXAMPLE. NOT A WORKING SKILL.

This is a scrubbed illustration accompanying the blog post "Add a Skip and a Note
to Every Question". Internal tool names, paths, and destinations have been replaced
with generic placeholders. It is here to show the *shape* of a skill that makes
every answer carry context; it is not wired to any real system and is not meant to run.
Fork and adapt if the ideas are useful.
-->

# Survey

## Overview

A survey is a plain Slack message: a title, some questions, and bullet options under each question. Nothing is stored in a service and no link triggers anything on its own. Authoring a survey means writing that message. Answering one means reading that message, walking the respondent through each question, and DMing their answers back to the author.

This keeps the survey independent of the skill. Anyone can author a survey by typing a message, whether or not they have this skill installed. Only the respondent needs the skill, to be guided through the questions and to post the answers.

The skill has two flows:

- **Author**: turn a request into a survey message and, optionally, post it to a Slack channel.
- **Respond**: read a survey message, ask the respondent each question, then DM the answers to the destination after they confirm.

## The survey message format

Surveys use a soft convention. Parse it best-effort and never block a respondent because a message is loosely formatted. When the structure is ambiguous, show the respondent how you parsed it and ask them to confirm before starting.

```
Survey: Tooling pulse check (Q2–Q3)
Results to: @johndoe

Which tool has been the most disappointing?

Which tool has been the most interesting?

Do you know how to set up a new project from scratch?
- Yes
- No

What's been your biggest pain point in Q2–Q3?

Answer survey at <permalink>
```

Parsing rules:

- A line starting with `Survey:` (or the first non-empty line) is the **title**.
- A line starting with `Results to:` names the **destination** (a `@handle`, a display name, or a channel). If absent, the destination defaults to whoever posted the survey.
- A line ending in `?` starts a **question**.
- Dash or bullet lines under a question are its **options**.
- A question with no options underneath is a **free-text question**: the respondent types an answer.
- Any other leading text is context and can be shown to the respondent as-is.

A messy paragraph with question marks still parses. The convention above just makes it crisp.

## Author flow

1. Collect the title, the questions, and the options for each question from the user's request. Ask for anything missing.
2. Confirm the destination for results. Default to the author (the person requesting the survey).
3. Render the survey message in the format above and show it to the user.
4. Ask whether to post it to Slack or hand it back as text to share themselves.
5. If posting, confirm the target channel, verify it is on the allowlist, then post with `post_message`. Report back the permalink.

End the posted message with a single call-to-action line: `Answer survey at <permalink>`. The respondent gives that link to their own `survey` skill, which reads the survey from it. Do not ask the respondent to copy or paste the message body; the link is the only handle they need, and reading the survey uses the same Slack access as sending the answers back, so if the skill can reach the link it can also post the reply.

The permalink only exists after the message is posted, so post first, then use `edit_message` to append the `Answer survey at <permalink>` line using the `permalink` from the post response.

Do not wrap the URL in mrkdwn styling. A trailing `_` (italics) placed right after a URL gets absorbed into the link and breaks it. Put the permalink on its own with plain text before it.

Keep questions short and options mutually exclusive where possible. Suggest merging near-duplicate options.

## Respond flow

1. Read the survey. The respondent gives a Slack link (the normal case; that is the `Answer survey at <permalink>` line from the posted survey). Fetch the message with the Slack read tools (`get_messages` / `get_thread`) and extract its text. Reading the survey and posting the answer back use the same Slack access, so a link is always enough; if the skill can read the link it can also send the reply. Accept pasted message text too if that is all the respondent has.
2. Parse it into a title, questions, options, and destination using the rules above. If parsing is ambiguous, show the parsed structure and ask the respondent to confirm or correct it.
3. Ask each question in turn, handling the two question kinds differently:

   **Multiple-choice questions** (the survey listed options): use a structured picker when the agent has one, a question tool that renders selectable options. Always append, after the survey's own options: **Skip** (no answer recorded) and **I don't know**. Keep a **free-text note** available too, so the respondent can characterize their choice; this is the whole point, so never drop it.

   **Free-text questions** (no options in the survey): just ask the question as plain text and let the respondent type their answer directly. Do not force them through a multiple-choice picker with an "Other" option, which is clumsy for an open question. Hint that they can also just say "skip" or "no clue" / "don't know", and capture those as `skipped` or `dont_know` rather than literal answers.

   When a batch of questions mixes both kinds, ask the free-text ones as plain prompts rather than dropping them into option pickers.
4. Support multi-select when a question allows more than one answer. When in doubt, ask whether the question is single- or multi-select.
5. Show a summary of all answers and let the respondent edit any of them before sending.
6. Confirm the destination and, only after the respondent says yes, DM the answers there.
7. After sending, ask if they want to keep a local copy of their responses. If yes, save to `~/surveys/responses/` (see Storage). If no, you're done; do not ask them for a path.

## Storage

Storage is optional and only happens if the respondent asks for it after sending (see the Respond flow). When they do, save the response as JSON so it can be re-sent or aggregated later. Use the location below directly; never ask the respondent to pick a path.

Location: `~/surveys/responses/`

Filename: `YYYY-MM-DDTHH-MM-SS-<survey-slug>-<user>.json`

Structure:

```json
{
  "timestamp": "2026-07-03T16:40:12.000Z",
  "respondent": "janedoe",
  "survey_title": "Tooling pulse check (Q2–Q3)",
  "destination": "@johndoe",
  "answers": [
    {
      "question": "Which tool has been the most disappointing?",
      "selected": ["Legacy dashboard"],
      "status": "answered",
      "note": null
    },
    {
      "question": "Which tool has been the most interesting?",
      "selected": ["The assistant"],
      "status": "answered",
      "note": "Great for quick lookups, less so for deep dives"
    },
    {
      "question": "Do you know how to set up a new project from scratch?",
      "selected": ["Yes"],
      "status": "answered",
      "note": null
    },
    {
      "question": "What's been your biggest pain point in Q2–Q3?",
      "selected": [],
      "status": "skipped",
      "note": null
    }
  ]
}
```

`status` is one of `answered`, `skipped`, or `dont_know`. `selected` holds the chosen options (or the typed answer for a free-text question) and is empty when skipped or unknown. `note` is the optional free-text context and is `null` when none was given.

## Sending results to Slack

Post the answers as a readable message to the destination:

- Resolve a `@handle` or name to a user with `lookup_user`, open a DM with `open_dm_channel`, and post with `post_message`.
- For a channel destination, post to the channel directly.
- Format the message with the survey title, the respondent, and one line per question showing the answer, its status, and any note.

Always confirm the destination with the respondent before posting. Never send without an explicit yes.

## Guardrails

- **Allowlist (authoring only).** When *authoring* a survey and posting it to a channel, read `~/.config/survey/allowlist.json` for the channels and people this skill may post to. If the file is missing, tell the user it needs to be created and show the format below; do not post a survey to an unlisted destination. This gate does **not** apply to the respond flow; a respondent sends their answers to whatever the survey's `Results to:` names, and the confirm-before-send step is the safety gate there. Don't make responders allowlist anything.
- **Confirm before every send.** Show the exact message and destination and wait for a yes. This is the safety gate; the person sees exactly what goes where before anything is posted.
- **Do not invent answers.** A skipped or unknown question stays that way in the sent message and in any saved copy.
- **Best-effort parsing, never a gate.** A loosely formatted survey still works; confirm the parse when unsure rather than refusing.

Allowlist format:

```json
{
  "channels": ["my-team-channel", "survey-results"],
  "people": ["johndoe", "janedoe"]
}
```

## Common mistakes

- **Dropping the note option.** Every question must allow a free-text note, even multiple-choice ones. This is the feature that gives answers their context.
- **Forcing a choice.** Skip and "I don't know" are always valid answers. Record them honestly.
- **Wrapping free-text questions in a picker.** Open questions have no options; ask them as plain text and let the respondent type. Don't make them pick "Other" to answer, but do hint they can say "skip" or "don't know".
- **Posting without confirmation.** Always show the message and destination and wait for a yes.
- **Treating the link as a trigger.** A Slack link is just a pointer to the survey message. Read the message from it; nothing runs on its own.
- **Asking the respondent to paste the whole message.** The link is the handle. Read the survey from it rather than making them copy the body.
- **Styling the permalink.** Never wrap the URL in mrkdwn (a trailing `_` breaks the link). Plain text before it, URL on its own.

## Quick reference

- **Trigger phrases:** "make a survey", "create a poll", "answer this survey", "run this survey", or a survey link/message.
- **Author output:** a Slack message in the survey format ending in `Answer survey at <permalink>`, optionally posted to a channel the author confirms.
- **Respond input:** the `Answer survey at <permalink>` link (or pasted text as a fallback).
- **Respond output:** a DM to the destination after confirmation, and an optional saved JSON copy in `~/surveys/responses/` if the respondent asks for one.
- **Multiple-choice questions offer:** the options, Skip, I don't know, and a free-text note.
- **Free-text questions:** asked as plain text; respondent types, or says "skip" / "don't know".
