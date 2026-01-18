#!/usr/bin/env python3
"""
Configuration for R2D2 Chatbot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for R2D2 Chatbot"""

    # Wake Word
    USE_WAKE_WORD = True
    PICOVOICE_API_KEY = os.getenv('PICOVOICE_API_KEY')
    PLATFORM = os.getenv('PLATFORM', 'linux')  # 'linux' or 'raspberry-pi'

    # Voice Settings
    TTS_VOICE = 'female'  # 'male' or 'female'
                          # female = en_US-ljspeech-high (HIGH quality, crystal clear)
                          # male = en_GB-alan-medium (British, clear)

    TTS_EFFECT = 'clear_transmission'  # Effects:
                                       # 'clear_transmission' - Clear + transmission feel (RECOMMENDED)
                                       # 'comlink' - Radio transmission with squelch
                                       # 'dramatic' - Deep narrator (Star Wars intro style)
                                       # 'radio' - Vintage radio effect
                                       # 'hologram' - Glitchy hologram
                                       # 'clear' - No effect

    # LLM Settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    LLM_MODEL = 'llama-3.1-8b-instant'  # Groq Llama 3.1 8B - Fast and free!

    # Whisper STT Settings
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'small')
    WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')
    WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'int8')

    # VAD Settings
    VAD_AGGRESSIVENESS = 2  # 0-3, higher = more aggressive (filters non-speech better)
    VAD_SPEECH_THRESHOLD = 8  # Frames of speech needed to start recording
    VAD_MIN_DURATION = 1.5  # Minimum recording duration in seconds

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if cls.USE_WAKE_WORD and not cls.PICOVOICE_API_KEY:
            raise ValueError("PICOVOICE_API_KEY required when USE_WAKE_WORD=True")

        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY required")

        return True
