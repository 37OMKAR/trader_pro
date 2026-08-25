"""
Market AI — Voice & Avatar Briefing REST Endpoints
Serves live neural TTS audio files and talking avatar briefing videos.
"""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.voice_engine.tts_engine import KokoroTTSEngine
from services.voice_engine.avatar_engine import TalkingAvatarEngine

router = APIRouter(prefix="/voice", tags=["Voice & Avatar Engine"])

tts_engine = KokoroTTSEngine()
avatar_engine = TalkingAvatarEngine()


class BriefingAudioRequest(BaseModel):
    text: str
    voice: Optional[str] = "en_in_male"


class AvatarVideoRequest(BaseModel):
    image_path: Optional[str] = "assets/presenter.png"
    script_text: str


@router.post("/synthesize-briefing")
async def synthesize_briefing(req: BriefingAudioRequest):
    return await tts_engine.synthesize_briefing_audio(req.text)


@router.post("/generate-avatar")
async def generate_avatar(req: AvatarVideoRequest):
    audio_res = await tts_engine.synthesize_briefing_audio(req.script_text)
    return await avatar_engine.generate_avatar_video(
        image_path=req.image_path or "assets/presenter.png",
        audio_path=audio_res["file_path"],
        script_text=req.script_text,
    )


@router.get("/stream/{filename}")
async def stream_audio(filename: str):
    """Streams generated MP3/WAV briefing audio file."""
    file_path = Path("artifacts/audio") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(file_path, media_type="audio/mpeg")


@router.get("/avatar-stream/{filename}")
async def stream_avatar_video(filename: str):
    """Streams rendered avatar video file."""
    file_path = Path("artifacts/avatar_videos") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Avatar video file not found.")
    return FileResponse(file_path, media_type="video/mp4")
