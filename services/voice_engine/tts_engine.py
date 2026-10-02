"""
Market AI — Kokoro TTS Voice Engine
Synthesizes natural speech audio market briefings and trade execution notices for Indian Dalal Street updates.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os
import asyncio
from datetime import datetime
from packages.market_calendar.calendar import IST_TIMEZONE


class KokoroTTSEngine:
    """Text-to-Speech synthesizer generating audio market digests and briefings."""

    def __init__(self, voice_name: str = "en_in_male"):
        self.voice_name = voice_name
        self.output_dir = Path("artifacts/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize_briefing_audio(
        self,
        text: str,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesizes text into audio MP3/WAV file with automated fallback."""
        if not filename:
            filename = f"briefing_{datetime.now(IST_TIMEZONE).strftime('%Y%m%d_%H%M%S')}.mp3"

        out_path = self.output_dir / filename

        # Try edge-tts / local Kokoro if available
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
            await communicate.save(str(out_path))
            return {
                "status": "SUCCESS",
                "engine": "edge-tts (en-IN-PrabhatNeural)",
                "file_path": str(out_path),
                "filename": filename,
                "duration_est_sec": round(len(text.split()) / 2.5, 1),
                "text_snippet": (text[:117] + "...") if len(text) > 120 else text,
            }
        except Exception as exc:
            # No TTS engine installed: write a valid silent-WAV placeholder so
            # downstream readers don't choke, and clearly flag that no real
            # audio was synthesized. Install `edge-tts` to enable real TTS.
            wav_path = out_path.with_suffix(".wav")
            duration_sec = max(1.0, round(len(text.split()) / 2.5, 1))
            self._write_silent_wav(wav_path, duration_sec)
            return {
                "status": "NO_ENGINE",
                "engine": "silent-wav-placeholder",
                "file_path": str(wav_path),
                "filename": wav_path.name,
                "duration_est_sec": duration_sec,
                "text_snippet": (text[:117] + "...") if len(text) > 120 else text,
                "error": str(exc),
                "hint": "pip install edge-tts  # for real en-IN voice synthesis",
            }

    @staticmethod
    def _write_silent_wav(path: Path, seconds: float, sample_rate: int = 16000) -> None:
        """Write a valid, playable mono 16-bit PCM silent WAV file."""
        import struct
        n_samples = int(seconds * sample_rate)
        data_size = n_samples * 2  # 16-bit mono
        with path.open("wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + data_size))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))         # PCM header size
            f.write(struct.pack("<H", 1))           # PCM format
            f.write(struct.pack("<H", 1))           # channels
            f.write(struct.pack("<I", sample_rate))
            f.write(struct.pack("<I", sample_rate * 2))  # byte rate
            f.write(struct.pack("<H", 2))           # block align
            f.write(struct.pack("<H", 16))          # bits/sample
            f.write(b"data")
            f.write(struct.pack("<I", data_size))
            f.write(b"\x00\x00" * n_samples)
