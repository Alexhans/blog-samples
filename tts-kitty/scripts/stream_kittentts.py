import argparse
from pathlib import Path
import queue
import re
import shutil
import tempfile
import threading

from audio_playback import play_audio_file
from cli_common import add_text_arguments, add_voice_model_arguments, resolve_text
from kittentts_generate import (
    DEFAULT_SAMPLE_RATE,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    add_text_arguments(parser)
    add_voice_model_arguments(parser)
    parser.add_argument(
        "--max-chars",
        type=int,
        default=450,
        help="Target max characters per chunk.",
    )
    parser.add_argument(
        "--prefetch",
        type=int,
        default=3,
        help="How many generated chunks to buffer ahead of playback.",
    )
    parser.add_argument(
        "--chunks-dir",
        help="Directory to write chunk WAV files. Uses a temp dir by default.",
    )
    parser.add_argument(
        "--keep-chunks",
        action="store_true",
        help="Keep chunk WAV files after playback.",
    )
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Generate chunks only, skip playback.",
    )
    return parser.parse_args(argv)


def split_long_text(text: str, max_chars: int) -> list[str]:
    parts: list[str] = []
    remaining = text.strip()
    while len(remaining) > max_chars:
        candidate = remaining[:max_chars]
        split_at = candidate.rfind(" ")
        if split_at <= 0:
            split_at = max_chars
        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def split_with_delimiters(text: str, max_chars: int) -> list[str]:
    fragments = re.split(r"(?<=[,;:])\s+", text.strip())
    if len(fragments) <= 1:
        return split_long_text(text, max_chars)

    chunks: list[str] = []
    current = ""
    for fragment in fragments:
        fragment = fragment.strip()
        if not fragment:
            continue
        candidate = f"{current} {fragment}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = fragment
        else:
            current = candidate

    if current:
        chunks.append(current)

    final_chunks: list[str] = []
    for chunk in chunks:
        if len(chunk) > max_chars:
            final_chunks.extend(split_long_text(chunk, max_chars))
        else:
            final_chunks.append(chunk)
    return final_chunks


def chunk_paragraph(paragraph: str, max_chars: int, segmenter: object) -> list[str]:
    paragraph = paragraph.strip()
    if not paragraph:
        return []
    if len(paragraph) <= max_chars:
        return [paragraph]

    sentences = [s.strip() for s in segmenter.segment(paragraph) if s.strip()]
    if not sentences:
        return split_with_delimiters(paragraph, max_chars)

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            oversized_parts = split_with_delimiters(sentence, max_chars)
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(oversized_parts)
            continue

        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def chunk_text(text: str, max_chars: int) -> list[str]:
    import pysbd

    segmenter = pysbd.Segmenter(language="en", clean=False)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: list[str] = []
    for paragraph in paragraphs:
        chunks.extend(chunk_paragraph(paragraph, max_chars=max_chars, segmenter=segmenter))
    return [chunk for chunk in chunks if chunk]


def producer(
    *,
    chunks: list[str],
    model: str,
    voice: str,
    sample_rate: int,
    chunks_dir: Path,
    chunk_queue: queue.Queue[Path | None],
) -> None:
    from kittentts import KittenTTS
    import soundfile as sf

    tts = KittenTTS(model)
    for idx, chunk in enumerate(chunks, start=1):
        audio = tts.generate(chunk, voice=voice)
        output_path = chunks_dir / f"chunk_{idx:04d}.wav"
        sf.write(output_path, audio, sample_rate)
        print(f"Generated chunk {idx}/{len(chunks)}: {output_path}")
        chunk_queue.put(output_path)
    chunk_queue.put(None)


def consumer(chunk_queue: queue.Queue[Path | None]) -> None:
    while True:
        item = chunk_queue.get()
        if item is None:
            break
        ok = play_audio_file(item)
        if not ok:
            print("Could not play audio (no supported system player found).")
            print("Generated chunks are still available on disk.")
            while chunk_queue.get() is not None:
                pass
            break


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    text = resolve_text(args)

    chunks = chunk_text(text, max_chars=args.max_chars)
    if not chunks:
        raise SystemExit("No text to synthesize after chunking.")

    use_temp_dir = args.chunks_dir is None
    if use_temp_dir:
        chunks_dir = Path(tempfile.mkdtemp(prefix="kittentts_chunks_"))
    else:
        chunks_dir = Path(args.chunks_dir)
        chunks_dir.mkdir(parents=True, exist_ok=True)

    print(f"Total chunks: {len(chunks)}")
    print(f"Chunks directory: {chunks_dir}")

    chunk_queue: queue.Queue[Path | None] = queue.Queue(maxsize=max(1, args.prefetch))
    producer_thread = threading.Thread(
        target=producer,
        kwargs={
            "chunks": chunks,
            "model": args.model,
            "voice": args.voice,
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "chunks_dir": chunks_dir,
            "chunk_queue": chunk_queue,
        },
        daemon=True,
    )

    producer_thread.start()
    try:
        if not args.no_play:
            consumer(chunk_queue)
    finally:
        producer_thread.join()
        if use_temp_dir and not args.keep_chunks:
            shutil.rmtree(chunks_dir, ignore_errors=True)

    print("Done.")


if __name__ == "__main__":
    main()
