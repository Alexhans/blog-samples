import argparse
from pathlib import Path

from audio_playback import play_audio_file
from cli_common import add_text_arguments, add_voice_model_arguments, resolve_text
from kittentts_generate import generate_wav


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    add_text_arguments(parser)
    add_voice_model_arguments(parser)
    parser.add_argument("--output", default="output.wav", help="Output WAV file path.")
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Generate audio but do not play it automatically.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    text = resolve_text(args)

    output_path = generate_wav(
        output_path=args.output,
        text=text,
        voice=args.voice,
        model=args.model,
    )
    print(f"Wrote audio to: {Path(output_path).resolve()}")

    if args.no_play:
        return

    if play_audio_file(output_path):
        print("Playback finished.")
    else:
        print("Audio written, but no supported audio player was found.")
        print("Install one of: ffplay, aplay, paplay, mpv (or afplay on macOS).")


if __name__ == "__main__":
    main()
