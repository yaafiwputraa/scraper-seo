from __future__ import annotations

import re
import subprocess
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import imageio_ffmpeg
from yt_dlp import YoutubeDL


def process_youtube_to_zip(
    url: str,
    segment_seconds: int = 10,
    upscale_4k: bool = True,
) -> tuple[bytes, str, int]:
    """
    Download one YouTube video, split it into clips, and return all clips as ZIP bytes.

    Args:
        url: YouTube video URL.
        segment_seconds: Duration of each clip in seconds.
        upscale_4k: If True, render clips at 4K (3840x2160).

    Returns:
        Tuple of (zip_bytes, zip_file_name, clip_count).
    """
    if not url.strip():
        raise ValueError("URL YouTube tidak boleh kosong.")

    if segment_seconds <= 0:
        raise ValueError("Durasi clip harus lebih dari 0 detik.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir)
        source_file = work_dir / "source.mp4"
        clips_dir = work_dir / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        title = _download_video(url=url, output_file=source_file)
        clip_base_name = _safe_name(title) if title else "youtube_video"

        if not source_file.exists():
            raise RuntimeError("Gagal menyiapkan file video sumber.")

        _split_video(
            input_file=source_file,
            clips_dir=clips_dir,
            segment_seconds=segment_seconds,
            upscale_4k=upscale_4k,
        )

        clip_files = sorted(clips_dir.glob("*.mp4"))
        if not clip_files:
            raise RuntimeError("Tidak ada clip yang berhasil dibuat.")

        zip_bytes = _build_zip(clip_files=clip_files, base_name=clip_base_name)
        suffix = "4k" if upscale_4k else "original"
        zip_name = f"{clip_base_name}_{segment_seconds}s_clips_{suffix}.zip"
        return zip_bytes, zip_name, len(clip_files)


def _download_video(url: str, output_file: Path) -> str:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(output_file),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": str(ffmpeg_path),  # Tambahkan baris ini
        "sleep_interval_requests": 1,
        "extractor_args": {"youtube": {"client": ["android", "web"]}},
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return str(info.get("title", "youtube_video"))
    except Exception as exc:
        raise RuntimeError(f"Gagal mengunduh video YouTube: {exc}") from exc


def _split_video(
    input_file: Path,
    clips_dir: Path,
    segment_seconds: int,
    upscale_4k: bool,
) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output_pattern = str(clips_dir / "clip_%03d.mp4")

    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_file),
        "-map_metadata",
        "-1",
        "-map_chapters",
        "-1",
    ]

    if upscale_4k:
        command.extend(["-vf", "scale=3840:2160:flags=lanczos,setsar=1"])

    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-force_key_frames",
            f"expr:gte(t,n_forced*{segment_seconds})",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-f",
            "segment",
            "-segment_time",
            str(segment_seconds),
            "-reset_timestamps",
            "1",
            output_pattern,
        ]
    )

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip() or "Unknown ffmpeg error"
        raise RuntimeError(f"Gagal memotong/render video: {error_text}")


def _build_zip(clip_files: list[Path], base_name: str) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for idx, clip_file in enumerate(clip_files, start=1):
            arc_name = f"{base_name}_clip_{idx:03d}.mp4"
            zip_file.write(clip_file, arcname=arc_name)

    return output.getvalue()


def _safe_name(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return sanitized[:80] if sanitized else "youtube_video"
