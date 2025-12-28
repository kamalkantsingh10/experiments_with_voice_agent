#!/usr/bin/env python3
"""
Piper TTS wrapper with British male and female voices
"""

from piper import PiperVoice
import wave
import io
import numpy as np
import sounddevice as sd
import soundfile as sf
import os
from pathlib import Path
import urllib.request
import json
from radio_effects import radio_effect, comlink_effect, hologram_effect


class PiperTTS:
    """Simple TTS class using Piper with British voices"""

    # British voice models
    VOICES = {
        'male': 'en_GB-alan-medium',      # British male voice
        'female': 'en_GB-alba-medium',    # British female voice
    }

    # Hugging Face model URLs
    HF_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
    VOICE_URLS = {
        'male': {
            'onnx': f"{HF_BASE_URL}/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
            'json': f"{HF_BASE_URL}/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json",
        },
        'female': {
            'onnx': f"{HF_BASE_URL}/en/en_GB/alba/medium/en_GB-alba-medium.onnx",
            'json': f"{HF_BASE_URL}/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json",
        },
    }

    def __init__(self, default_voice='female', models_dir='./piper_models'):
        """
        Initialize Piper TTS

        Args:
            default_voice: 'male' or 'female' (default: 'female')
            models_dir: Directory to store voice models (default: './piper_models')
        """
        self.default_voice = default_voice
        self.voices_loaded = {}
        self.sample_rate = 22050  # Piper default sample rate
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        print(f"Initializing Piper TTS (default: {default_voice})")
        print(f"Models directory: {self.models_dir}")

    def _download_voice(self, voice_type):
        """Download voice model files from Hugging Face if not present"""
        model_name = self.VOICES[voice_type]
        onnx_path = self.models_dir / f"{model_name}.onnx"
        json_path = self.models_dir / f"{model_name}.onnx.json"

        # Check if already downloaded
        if onnx_path.exists() and json_path.exists():
            return str(onnx_path)

        print(f"Downloading {voice_type} voice model ({model_name})...")
        print("This may take a few minutes (50-250MB)...")

        # Download ONNX model
        if not onnx_path.exists():
            print(f"  Downloading {model_name}.onnx...")
            urllib.request.urlretrieve(
                self.VOICE_URLS[voice_type]['onnx'],
                onnx_path
            )
            print(f"  ✓ ONNX model downloaded")

        # Download JSON config
        if not json_path.exists():
            print(f"  Downloading {model_name}.onnx.json...")
            urllib.request.urlretrieve(
                self.VOICE_URLS[voice_type]['json'],
                json_path
            )
            print(f"  ✓ Config downloaded")

        print(f"✓ {voice_type.capitalize()} voice ready")
        return str(onnx_path)

    def _load_voice(self, voice_type):
        """Load a voice model if not already loaded"""
        if voice_type not in self.voices_loaded:
            model_name = self.VOICES[voice_type]
            print(f"Loading {voice_type} voice: {model_name}")

            # Download if needed
            model_path = self._download_voice(voice_type)

            # Load the voice
            self.voices_loaded[voice_type] = PiperVoice.load(
                model_path,
                config_path=str(self.models_dir / f"{model_name}.onnx.json")
            )
            print(f"✓ {voice_type.capitalize()} voice loaded")

        return self.voices_loaded[voice_type]

    def generate(self, text, voice=None):
        """
        Generate speech from text

        Args:
            text: Text to speak
            voice: 'male' or 'female' (uses default if not specified)

        Returns:
            numpy array of audio samples (float32, -1.0 to 1.0)
        """
        voice_type = voice or self.default_voice

        if voice_type not in self.VOICES:
            raise ValueError(f"Voice must be 'male' or 'female', got: {voice_type}")

        # Load voice
        piper_voice = self._load_voice(voice_type)

        # Collect audio chunks from synthesize generator
        audio_chunks = []
        for chunk in piper_voice.synthesize(text):
            # Get int16 audio array from AudioChunk
            audio_chunks.append(chunk.audio_int16_array)

        # Combine all chunks
        audio = np.concatenate(audio_chunks)

        # Convert to float (-1.0 to 1.0)
        audio = audio.astype(np.float32) / 32768.0

        # Get sample rate from voice config
        self.sample_rate = piper_voice.config.sample_rate

        return audio

    def apply_effect(self, audio, effect='clear'):
        """
        Apply a communication channel effect to audio

        Args:
            audio: Audio array (float32, -1.0 to 1.0)
            effect: Effect type - 'clear', 'radio', 'comlink', or 'hologram'

        Returns:
            Processed audio
        """
        if effect == 'clear':
            return audio
        elif effect == 'radio':
            return radio_effect(audio, self.sample_rate)
        elif effect == 'comlink':
            return comlink_effect(audio, self.sample_rate)
        elif effect == 'hologram':
            return hologram_effect(audio, self.sample_rate)
        else:
            raise ValueError(f"Unknown effect: {effect}. Use 'clear', 'radio', 'comlink', or 'hologram'")

    def speak(self, text, voice=None, effect='clear'):
        """
        Generate and play speech

        Args:
            text: Text to speak
            voice: 'male' or 'female' (uses default if not specified)
            effect: Audio effect - 'clear', 'radio', 'comlink', or 'hologram'
        """
        print(f"Speaking: \"{text}\" (voice: {voice or self.default_voice}, effect: {effect})")
        audio = self.generate(text, voice)

        # Apply effect if specified
        if effect != 'clear':
            audio = self.apply_effect(audio, effect)

        self.play(audio)

    def play(self, audio):
        """Play audio through speakers"""
        sd.play(audio, self.sample_rate)
        sd.wait()

    def save(self, text, filename, voice=None):
        """
        Generate speech and save to WAV file

        Args:
            text: Text to speak
            filename: Output WAV filename
            voice: 'male' or 'female' (uses default if not specified)
        """
        audio = self.generate(text, voice)

        # Convert back to int16 for WAV file
        audio_int16 = (audio * 32767).astype(np.int16)

        # Save to file
        with wave.open(filename, 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.sample_rate)
            wav.writeframes(audio_int16.tobytes())

        print(f"✓ Saved to {filename}")


# Demo usage
if __name__ == "__main__":
    print("=" * 60)
    print("PIPER TTS - BRITISH VOICES WITH RADIO EFFECTS")
    print("=" * 60)
    print()

    # Initialize TTS
    tts = PiperTTS(default_voice='female')

    # Test female voice with different effects
    print("\n--- British Female Voice ---")
    tts.speak("Hello, this is a clear transmission.", voice='female', effect='clear')

    print("\n--- With Radio Effect ---")
    tts.speak("This is a radio transmission.", voice='female', effect='radio')

    print("\n--- With Comlink Effect ---")
    tts.speak("Comlink activated, come in commander.", voice='female', effect='comlink')

    print("\n--- With Hologram Effect ---")
    tts.speak("Help me Obi-Wan Kenobi, you're my only hope.", voice='female', effect='hologram')

    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
