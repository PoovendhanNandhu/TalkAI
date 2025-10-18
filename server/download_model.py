#!/usr/bin/env python3
"""Pre-download TTS model with license acceptance."""
import os
os.environ['COQUI_TOS_AGREED'] = '1'

from TTS.api import TTS

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
print(f"[Download] Loading {MODEL_NAME}...")
print("[Download] By running this, you agree to Coqui TTS license terms:")
print("[Download] Non-commercial CPML: https://coqui.ai/cpml")

tts_model = TTS(MODEL_NAME)
print("[Download] Model downloaded successfully!")
