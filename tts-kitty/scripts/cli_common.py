import argparse
from pathlib import Path

from kittentts_generate import (
    AVAILABLE_MODELS,
    AVAILABLE_VOICES,
    DEFAULT_MODEL,
    DEFAULT_TEXT,
    DEFAULT_VOICE,
)


def add_text_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Text to synthesize.")
    parser.add_argument(
        "--text-file",
        help="Path to a text file to synthesize. Overrides --text when provided.",
    )


def add_voice_model_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        choices=AVAILABLE_VOICES,
        help="Voice to use.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help="Hugging Face model ID to load.",
    )


def resolve_text(args: argparse.Namespace) -> str:
    if args.text_file:
        return Path(args.text_file).read_text(encoding="utf-8")
    return args.text
