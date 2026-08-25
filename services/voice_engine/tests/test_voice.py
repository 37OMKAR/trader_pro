"""
Unit tests for Kokoro TTS Voice and Avatar Engine.
"""

import pytest
from services.voice_engine.tts_engine import KokoroTTSEngine
from services.voice_engine.avatar_engine import TalkingAvatarEngine


@pytest.mark.anyio
async def test_tts_briefing_synthesis():
    tts = KokoroTTSEngine()
    result = await tts.synthesize_briefing_audio(
        text="Good morning Dalal Street. NIFTY 50 opens flat at 24,500.",
        filename="test_briefing.mp3",
    )
    assert result["status"] == "SUCCESS"
    assert "file_path" in result
    assert result["duration_est_sec"] > 0


@pytest.mark.anyio
async def test_avatar_video_generation():
    avatar = TalkingAvatarEngine()
    result = await avatar.generate_avatar_video(
        image_path="assets/presenter.png",
        audio_path="artifacts/audio/test_briefing.mp3",
        script_text="NIFTY 50 trading in bullish regime.",
        filename="test_avatar.mp4",
    )
    assert result["status"] == "SUCCESS"
    assert "video_path" in result
