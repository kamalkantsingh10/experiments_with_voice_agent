#!/usr/bin/env python3
"""
Wake Word Detection using Porcupine
Listens for "Hey Olaf" to activate the voice agent
"""

import os
import struct
import pvporcupine
import pyaudio
from dotenv import load_dotenv


class WakeWordListener:
    """
    Listens for wake word using Porcupine (fully local, free)
    Supports platform-specific wake words via .env configuration
    """

    def __init__(self, keyword=None, access_key=None):
        """
        Initialize wake word listener

        Args:
            keyword: Override wake word (built-in name or .ppn path)
                    If None, uses PLATFORM from .env to auto-select
            access_key: Picovoice API key (loaded from .env if not provided)
        """
        # Load environment variables
        load_dotenv()

        # Get API key
        self.access_key = access_key or os.getenv('PICOVOICE_API_KEY')
        if not self.access_key:
            raise ValueError(
                "Picovoice API key not found. "
                "Set PICOVOICE_API_KEY in .env file or pass as argument."
            )

        # Determine wake word based on platform
        platform = os.getenv('PLATFORM', 'linux').lower()

        if keyword is None:
            if platform == 'raspberry-pi':
                # Use custom Hey Olaf file on Raspberry Pi
                keyword = os.path.join(
                    os.path.dirname(__file__),
                    'wake_words',
                    'Hey-Olaf_en_raspberry-pi_v4_0_0.ppn'
                )
                self.use_builtin = False
                self.wake_word_name = "Hey Olaf"
            else:
                # Use Alexa on Linux/desktop
                keyword = 'alexa'
                self.use_builtin = True
                self.wake_word_name = "Alexa"
        else:
            # Manual override
            # Check if it's a built-in keyword
            builtin_keywords = ['porcupine', 'jarvis', 'computer', 'hey google', 'hey siri', 'alexa']
            if keyword.lower() in builtin_keywords:
                self.use_builtin = True
                self.wake_word_name = keyword.title()
            else:
                self.use_builtin = False
                self.wake_word_name = "Custom"

        # Store keyword
        if self.use_builtin:
            self.keyword = keyword.lower()
            self.keyword_path = None
            print(f"Wake word listener initialized")
            print(f"Platform: {platform}")
            print(f"Wake word: '{self.wake_word_name}' (built-in)")
        else:
            # Custom .ppn file
            if not os.path.isabs(keyword):
                keyword = os.path.join(
                    os.path.dirname(__file__),
                    'wake_words',
                    keyword
                )

            if not os.path.exists(keyword):
                raise FileNotFoundError(f"Wake word file not found: {keyword}")

            self.keyword = None
            self.keyword_path = keyword
            print(f"Wake word listener initialized")
            print(f"Platform: {platform}")
            print(f"Wake word: '{self.wake_word_name}'")
            print(f"Keyword file: {keyword}")

        self.porcupine = None
        self.audio_stream = None

    def start(self, callback=None, sensitivity=0.5, stop_on_detect=False):
        """
        Start listening for wake word

        Args:
            callback: Function to call when wake word is detected
            sensitivity: Detection sensitivity (0.0 to 1.0)
            stop_on_detect: Stop listening after first detection (default: False)
        """
        try:
            # Initialize Porcupine with either built-in keyword or custom file
            if self.use_builtin:
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=[self.keyword],
                    sensitivities=[sensitivity]
                )
            else:
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.keyword_path],
                    sensitivities=[sensitivity]
                )

            # Initialize PyAudio
            pa = pyaudio.PyAudio()

            self.audio_stream = pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            print(f"\n🎤 Listening for '{self.wake_word_name}'...")
            if not stop_on_detect:
                print("Press Ctrl+C to stop\n")

            while True:
                # Read audio
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                # Process audio
                keyword_index = self.porcupine.process(pcm)

                # Wake word detected
                if keyword_index >= 0:
                    print(f"✓ Wake word detected: {self.wake_word_name}!")
                    if callback:
                        callback()

                    # Stop if requested
                    if stop_on_detect:
                        break

        except KeyboardInterrupt:
            print("\n\nStopping wake word listener...")
        finally:
            self.stop()

    def stop(self):
        """Clean up resources"""
        if self.audio_stream is not None:
            self.audio_stream.close()
        if self.porcupine is not None:
            self.porcupine.delete()
        print("Wake word listener stopped")


# Demo
if __name__ == "__main__":
    listener = WakeWordListener()

    def on_wake_word():
        """Called when wake word is detected"""
        print("  → Waking up OLAF agent...")
        print("  → Ready for command!\n")
        print(f"🎤 Listening for '{listener.wake_word_name}'...")

    listener.start(callback=on_wake_word, sensitivity=0.5)
