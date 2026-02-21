from pathlib import Path

DEFAULT_MODEL = "KittenML/kitten-tts-mini-0.8"
DEFAULT_VOICE = "Jasper"
DEFAULT_TEXT = "This high quality TTS model works without a GPU"
DEFAULT_SAMPLE_RATE = 24000
AVAILABLE_VOICES = [
    "Bella",
    "Jasper",
    "Luna",
    "Bruno",
    "Rosie",
    "Hugo",
    "Kiki",
    "Leo",
]
AVAILABLE_MODELS = [
    "KittenML/kitten-tts-mini-0.8",
    "KittenML/kitten-tts-micro-0.8",
    "KittenML/kitten-tts-nano-0.8",
    "KittenML/kitten-tts-nano-0.8-int8",
]


def generate_wav(
    output_path: str | Path = "output.wav",
    text: str = DEFAULT_TEXT,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> Path:
    from kittentts import KittenTTS
    import soundfile as sf

    model_instance = KittenTTS(model)
    audio = model_instance.generate(text, voice=voice)

    output = Path(output_path)
    sf.write(output, audio, sample_rate)
    return output
