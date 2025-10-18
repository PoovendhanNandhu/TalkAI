# FastAPI backend for self-hosted Hinglish (Hindi+English) Text-to-Speech
# System deps required at runtime: ffmpeg, libsndfile
# pip installs: torch (CPU), TTS, fastapi, uvicorn[standard], pydub, regex, soundfile, numpy

import os
os.environ['COQUI_TOS_AGREED'] = '1'

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from typing import List
from io import BytesIO
from pydub import AudioSegment
import regex as re

# Configure ffmpeg path for pydub
# On macOS (Homebrew), use /opt/homebrew/bin/ffmpeg
# On Linux (Docker), ffmpeg is in PATH
import shutil
ffmpeg_path = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
ffprobe_path = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Load Coqui XTTS v2 (open-source, multilingual) once at startup
from TTS.api import TTS
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
print("[Boot] Loading Coqui XTTS v2… (first run may download model files)")
tts_model = TTS(MODEL_NAME)

app = FastAPI(title="Self-hosted Hinglish TTS", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Detect Devanagari vs Latin to route segments
DEVANAGARI_RE = re.compile(r"[\p{Devanagari}]+", re.UNICODE)

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=6000)
    speed: float = Field(1.0, description="Playback speed multiplier (post-process)")
    pause_ms: int = Field(160, description="Pause inserted between segments")

class Segment(BaseModel):
    text: str
    lang: str  # 'hi' or 'en'

class TTSResponse(BaseModel):
    segments: List[Segment]

def detect_lang(token: str) -> str:
    return "hi" if DEVANAGARI_RE.search(token) else "en"

def segment_text(text: str) -> List[Segment]:
    tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    segments: List[Segment] = []
    buf = []
    current_lang = None
    for tok in tokens:
        lang = detect_lang(tok)
        if current_lang is None:
            current_lang = lang; buf.append(tok)
        elif lang == current_lang or re.match(r"^\W$", tok):
            buf.append(tok)
        else:
            segments.append(Segment(text="".join(buf), lang=current_lang))
            buf = [tok]; current_lang = lang
    if buf:
        segments.append(Segment(text="".join(buf), lang=current_lang))
    return segments

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@app.post("/segments", response_model=TTSResponse)
async def preview_segments(req: TTSRequest):
    return TTSResponse(segments=segment_text(req.text))

@app.post("/tts")
async def tts(req: TTSRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Empty text")

    segs = segment_text(text)
    if not segs:
        raise HTTPException(400, "No segments")

    try:
        final = AudioSegment.silent(duration=0)
        pause = AudioSegment.silent(duration=max(0, req.pause_ms))

        import numpy as np
        import soundfile as sf

        for seg in segs:
            lang = seg.lang  # 'hi' or 'en'
            # XTTS v2 requires speaker parameter - using built-in "Claribel Dervla" speaker
            wav = tts_model.tts(text=seg.text, language=lang, speaker="Claribel Dervla")  # numpy float waveform
            buf = BytesIO()
            # XTTS v2 uses 24kHz sample rate
            sr = 24000 if hasattr(wav, '__len__') else tts_model.synthesizer.output_sample_rate
            sf.write(buf, wav if isinstance(wav, np.ndarray) else np.array(wav), samplerate=sr, format="WAV")
            buf.seek(0)
            clip = AudioSegment.from_file(buf, format="wav")
            if abs(req.speed - 1.0) > 1e-3:
                clip = clip._spawn(
                    clip.raw_data,
                    overrides={"frame_rate": int(clip.frame_rate * req.speed)}
                ).set_frame_rate(clip.frame_rate)
            final += clip + pause

        out = BytesIO()
        final.export(out, format="mp3", bitrate="128k")
        out.seek(0)
        headers = {"x-tts-segments": ",".join([f"{s.lang}:{len(s.text)}" for s in segs])}
        return StreamingResponse(out, media_type="audio/mpeg", headers=headers)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Synthesis failed: {e}")
