from pathlib import Path
import shutil
import subprocess
import sys


def play_audio_file(path: str | Path) -> bool:
    audio_path = Path(path)

    players: list[list[str]] = []
    if sys.platform == "darwin":
        players.append(["afplay", str(audio_path)])
    else:
        players.extend(
            [
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(audio_path)],
                ["aplay", str(audio_path)],
                ["paplay", str(audio_path)],
                ["mpv", "--no-video", str(audio_path)],
            ]
        )

    for command in players:
        if shutil.which(command[0]):
            completed = subprocess.run(command, check=False)
            return completed.returncode == 0

    return False
