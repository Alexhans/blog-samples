# tts-kitty

Simple KittenTTS demo with:
- one-shot generation/playback
- streaming generation/playback for large text
- model switching (mini/micro/nano/int8)

## What This Sample Shows

This project came out of an iterative conversation:
- start with a minimal KittenTTS script
- add model and voice options
- add text-file input
- add semantic chunking (`pysbd`) + streaming playback
- refactor to reduce duplication and provide one clear runner entry point

## Install

Preferred (tool-agnostic) setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Optional: Hatch also works, but it is not required for this sample.

## Quick Start (One Runner)

Use this as the main entry point:

```bash
python scripts/run_tts.py <mode> [options]
```

Modes:
- `once`: one-shot generation (optionally auto-play)
- `stream`: semantic chunking + streaming playback

Examples:

```bash
python scripts/run_tts.py once --text "Hello world"
python scripts/run_tts.py once --text-file input.md --model KittenML/kitten-tts-micro-0.8
python scripts/run_tts.py stream --text-file input.md --model KittenML/kitten-tts-nano-0.8-int8
python scripts/run_tts.py once --help
python scripts/run_tts.py stream --help
```

## Direct Scripts

```bash
python scripts/generate_kittentts.py
```

This writes `output.wav` and then tries to play it using an available system player.

## Streaming Large Text

For large inputs, use the streaming script. It chunks text semantically:

- Paragraphs first
- Then sentence boundaries via `pysbd`
- Then clause/space fallback only when needed

This lets generation and playback run in parallel, so you start hearing output before the full file is finished.

```bash
python scripts/stream_kittentts.py --text-file input.md
```

Useful streaming options:

- `--max-chars`: soft chunk size ceiling (default `450`)
- `--prefetch`: number of chunk WAVs buffered ahead of playback (default `3`)
- `--chunks-dir`: write chunks to a specific folder
- `--keep-chunks`: keep chunk WAVs after completion
- `--no-play`: generate chunks only

## CLI Options

```bash
python scripts/generate_kittentts.py --help
python scripts/stream_kittentts.py --help
```

Options:

- `--text`: Text to synthesize.
- `--text-file`: Path to a text file to synthesize. Overrides `--text` when provided.
- `--voice`: Voice to use. Choices are:
  - `Bella`
  - `Jasper`
  - `Luna`
  - `Bruno`
  - `Rosie`
  - `Hugo`
  - `Kiki`
  - `Leo`
- `--model`: Hugging Face model ID. Choices are:
  - `KittenML/kitten-tts-mini-0.8` (80M, ~80MB)
  - `KittenML/kitten-tts-micro-0.8` (40M, ~41MB)
  - `KittenML/kitten-tts-nano-0.8` (15M, ~56MB)
  - `KittenML/kitten-tts-nano-0.8-int8` (15M, ~25MB)
- `--output`: Output WAV file path (default: `output.wav`).
- `--no-play`: Generate audio only, skip playback.

## Examples

```bash
python scripts/generate_kittentts.py --voice Bella --text "Hello world"
python scripts/generate_kittentts.py --text-file input.md
python scripts/generate_kittentts.py --model KittenML/kitten-tts-mini-0.8
python scripts/generate_kittentts.py --model KittenML/kitten-tts-micro-0.8
python scripts/generate_kittentts.py --model KittenML/kitten-tts-nano-0.8
python scripts/generate_kittentts.py --model KittenML/kitten-tts-nano-0.8-int8
python scripts/generate_kittentts.py --output demo.wav
python scripts/generate_kittentts.py --no-play
python scripts/stream_kittentts.py --text-file input.md --model KittenML/kitten-tts-nano-0.8-int8
python scripts/stream_kittentts.py --text-file input.md --max-chars 380 --prefetch 4
```
