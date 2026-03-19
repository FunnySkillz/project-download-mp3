# project-download-mp3

Download YouTube audio as MP3 files using a simple URL list in `Url.txt`.

## What this project does

- Reads URLs from `Url.txt`
- Decides per URL whether to download:
  - a single video, or
  - a full playlist
- Runs `yt-dlp` to extract audio and convert it to MP3
- Saves files to `downloads/` as:
  - `Title [VideoID].mp3`

## How it works

1. `download_mp3.py` loads `Url.txt` and reads one entry per line.
2. Empty lines and comment lines (`# ...`) are ignored.
3. Each line is interpreted as one of these modes:
  - `single <url>`: force single-video download
  - `playlist <url>`: force playlist download
  - `<url>` (no prefix): auto mode
4. In auto mode:
  - playlist-style URL (`/playlist?...`) => download playlist
  - URL with `list=` but without `v=` => download playlist
  - otherwise => download only one video
5. The script checks for `ffmpeg`:
  - first from system `PATH`
  - then from common WinGet install location
6. For each entry, it runs:
  - `python -m yt_dlp -x --audio-format mp3 --audio-quality 0 ...`
7. Files are written to `downloads/`.

## Requirements

- Python 3.10+ (3.11+ recommended)
- `yt-dlp` Python package
- `ffmpeg` installed and available

## Setup

Install dependency:

```bash
pip install yt-dlp
```

Install ffmpeg (Windows options):

- Winget: `winget install Gyan.FFmpeg`
- or download manually and add `ffmpeg/bin` to `PATH`

## Usage

1. Edit `Url.txt` and add your URLs.
2. Run:

```bash
python download_mp3.py
```

3. Check generated MP3 files in `downloads/`.

## `Url.txt` format

```text
# Auto mode examples
https://www.youtube.com/watch?v=VIDEO_ID
https://www.youtube.com/playlist?list=PLAYLIST_ID

# Forced behavior
single https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
playlist https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
```

## Notes

- `downloads/` is ignored in git, so generated audio files are not committed.
- If one URL fails, the script exits with that error code.

## Troubleshooting

- `Missing file: ... Url.txt`: create `Url.txt` in the project root.
- `No URLs found in Url.txt.`: add at least one non-empty, non-comment line.
- `ffmpeg was not found in PATH.`: install ffmpeg and ensure it is accessible from terminal.
