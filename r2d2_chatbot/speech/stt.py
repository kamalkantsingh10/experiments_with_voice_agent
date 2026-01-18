#!/usr/bin/env python3
"""
Whisper Speech-to-Text for OLAF Voice Agent
Uses faster-whisper for efficient transcription
"""

from faster_whisper import WhisperModel
import numpy as np
import os
from dotenv import load_dotenv


class WhisperSTT:
    """
    Speech-to-Text using Faster Whisper
    Optimized for real-time voice agent applications
    """

    def __init__(self, model_size=None, device=None, compute_type=None):
        """
        Initialize Whisper STT

        Args:
            model_size: Model size - 'tiny', 'base', 'small', 'medium', 'large'
                       If None, loads from .env (default: 'small')
            device: 'cpu' or 'cuda' (default: from .env or 'cpu')
            compute_type: Quantization - 'int8', 'float16', 'float32'
                         (default: from .env or 'int8')
        """
        # Load environment variables
        load_dotenv()

        # Get configuration from .env or use defaults
        self.model_size = model_size or os.getenv('WHISPER_MODEL', 'small')
        self.device = device or os.getenv('WHISPER_DEVICE', 'cpu')
        self.compute_type = compute_type or os.getenv('WHISPER_COMPUTE_TYPE', 'int8')

        print(f"Initializing Whisper STT")
        print(f"  Model: {self.model_size}")
        print(f"  Device: {self.device}")
        print(f"  Compute type: {self.compute_type}")

        # Initialize Whisper model
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )

        print("✓ Whisper STT ready")

    def transcribe(self, audio_data, sample_rate=16000, language=None):
        """
        Transcribe audio to text

        Args:
            audio_data: Audio data as numpy array (float32, -1.0 to 1.0)
                       or path to audio file
            sample_rate: Sample rate of audio (default: 16000)
            language: Language code (e.g., 'en') or None for auto-detect

        Returns:
            dict with 'text' and 'language' keys
        """
        # If audio_data is a string, it's a file path
        if isinstance(audio_data, str):
            segments, info = self.model.transcribe(
                audio_data,
                language=language,
                beam_size=5
            )
        else:
            # Convert numpy array to the format Whisper expects
            # Ensure it's float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Transcribe from numpy array
            segments, info = self.model.transcribe(
                audio_data,
                language=language,
                beam_size=5
            )

        # Collect all segments
        full_text = ""
        for segment in segments:
            full_text += segment.text

        return {
            'text': full_text.strip(),
            'language': info.language,
            'language_probability': info.language_probability
        }

    def transcribe_streaming(self, audio_data, sample_rate=16000, language=None):
        """
        Transcribe audio with streaming results (yields segments as they come)

        Args:
            audio_data: Audio data as numpy array (float32, -1.0 to 1.0)
            sample_rate: Sample rate of audio (default: 16000)
            language: Language code (e.g., 'en') or None for auto-detect

        Yields:
            dict with 'text', 'start', 'end' for each segment
        """
        # Ensure it's float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Transcribe from numpy array
        segments, info = self.model.transcribe(
            audio_data,
            language=language,
            beam_size=5
        )

        # Yield segments as they come
        for segment in segments:
            yield {
                'text': segment.text.strip(),
                'start': segment.start,
                'end': segment.end
            }


# Demo usage
if __name__ == "__main__":
    import sounddevice as sd
    import time

    print("=" * 60)
    print("WHISPER STT DEMO")
    print("=" * 60)
    print()

    # Initialize STT
    stt = WhisperSTT()

    # Record audio
    SAMPLE_RATE = 16000
    DURATION = 5

    print(f"Recording {DURATION} seconds of audio...")
    print("Speak now!\n")
    print("Recording starts in 3 seconds...")
    time.sleep(3)

    print("🔴 RECORDING...")
    audio_data = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    print("✓ Recording complete!\n")

    # Transcribe
    print("Transcribing...")
    start_time = time.time()
    result = stt.transcribe(audio_data.squeeze(), SAMPLE_RATE)
    transcription_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("TRANSCRIPTION RESULT")
    print("=" * 60)
    print(f"Text: {result['text']}")
    print(f"Language: {result['language']} ({result['language_probability']:.2%})")
    print(f"Transcription time: {transcription_time:.2f}s")
    print("=" * 60)
