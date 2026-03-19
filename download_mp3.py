from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def parse_url_entries(url_file: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw_line in url_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        lowered = line.lower()
        if lowered.startswith("playlist "):
            url = line[len("playlist ") :].strip()
            if url:
                entries.append(("playlist", url))
            continue

        if lowered.startswith("single "):
            url = line[len("single ") :].strip()
            if url:
                entries.append(("single", url))
            continue

        entries.append(("auto", line))

    return entries


def should_download_as_playlist(mode: str, url: str) -> bool:
    if mode == "playlist":
        return True
    if mode == "single":
        return False

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    path = parsed.path.rstrip("/").lower()

    if path.endswith("/playlist"):
        return True

    if "list" in query and "v" not in query:
        return True

    return False


def resolve_ffmpeg_bin_dir() -> str | None:
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        return str(Path(ffmpeg_in_path).parent)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_root = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        winget_hits = sorted(
            winget_root.glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"),
            reverse=True,
        )
        if winget_hits:
            return str(winget_hits[0].parent)

    return None


def main() -> int:
    project_root = Path(__file__).resolve().parent
    url_file = project_root / "Url.txt"
    download_dir = project_root / "downloads"

    if not url_file.exists():
        print(f"Missing file: {url_file}")
        print("Create Url.txt and add one YouTube URL per line.")
        return 1

    entries = parse_url_entries(url_file)
    if not entries:
        print("No URLs found in Url.txt.")
        print("Add one YouTube URL per line, then run this script again.")
        return 1

    ffmpeg_bin_dir = resolve_ffmpeg_bin_dir()
    if ffmpeg_bin_dir is None:
        print("ffmpeg was not found in PATH.")
        print("Install ffmpeg first, then run this script again.")
        return 1

    download_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if ffmpeg_bin_dir not in env.get("PATH", ""):
        env["PATH"] = f"{ffmpeg_bin_dir}{os.pathsep}{env.get('PATH', '')}"

    print(f"Starting download + mp3 conversion for {len(entries)} item(s)...")

    output_template = str(download_dir / "%(title)s [%(id)s].%(ext)s")
    for index, (mode, url) in enumerate(entries, start=1):
        as_playlist = should_download_as_playlist(mode, url)
        mode_label = "playlist" if as_playlist else "single"
        print(f"[{index}/{len(entries)}] Processing as {mode_label}: {url}")

        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
        ]
        if not as_playlist:
            cmd.append("--no-playlist")
        cmd.extend(
            [
                "-o",
                output_template,
                url,
            ]
        )

        result = subprocess.run(cmd, cwd=project_root, env=env)
        if result.returncode != 0:
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
