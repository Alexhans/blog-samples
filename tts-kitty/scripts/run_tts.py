import sys

import generate_kittentts
import stream_kittentts

USAGE = """\
Usage:
  python scripts/run_tts.py once [once-options]
  python scripts/run_tts.py stream [stream-options]

Examples:
  python scripts/run_tts.py once --text "Hello world"
  python scripts/run_tts.py stream --text-file input.md --model KittenML/kitten-tts-nano-0.8-int8
"""


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(USAGE.rstrip())
        return

    mode = args[0]
    remaining = args[1:]
    if mode == "once":
        generate_kittentts.main(remaining)
        return
    if mode == "stream":
        stream_kittentts.main(remaining)
        return

    raise SystemExit(f"Unknown mode: {mode}\n\n{USAGE}")


if __name__ == "__main__":
    main()
