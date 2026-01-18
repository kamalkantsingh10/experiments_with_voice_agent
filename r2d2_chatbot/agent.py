#!/usr/bin/env python3
"""
R2D2 Chatbot Agent - Bumblebee-style Communication
Main agent class that orchestrates all components
"""

import threading
import time
import sounddevice as sd

from r2d2_chatbot.config import Config
from r2d2_chatbot.audio.wakeword import WakeWordListener
from r2d2_chatbot.audio.vad import VADRecorder
from r2d2_chatbot.speech.stt import WhisperSTT
from r2d2_chatbot.speech.tts.piper import PiperTTS
from r2d2_chatbot.speech.tts.r2d2 import R2D2WordVocabulary
from r2d2_chatbot.llm.groq_client import GroqClient


class R2D2ChatbotAgent:
    """
    R2D2 Chatbot Agent - Bumblebee-style Communication
    - Wake word detection (Alexa/Hey Olaf)
    - VAD-based recording (stops when you stop speaking)
    - Speech-to-Text (Whisper)
    - LLM (Groq Llama) - Returns structured R2D2 + info messages
    - Bumblebee-style Hybrid TTS:
      * Primary: R2D2 chirps/beeps (conversational responses)
      * Secondary: Clear transmission (specific information delivery)
      * Uses en_US-ljspeech-high (HIGH quality female voice)
    """

    def __init__(self, config=None):
        """
        Initialize R2D2 Chatbot Agent

        Args:
            config: Config object (uses default if None)
        """
        self.config = config or Config()
        self.config.validate()

        print("=" * 60)
        print("INITIALIZING R2D2 CHATBOT")
        print("=" * 60)
        print()

        # Initialize components
        self._init_components()

        # Agent state
        self.is_awake = False
        self.wake_thread = None
        self.wake_stop_event = threading.Event()

        print()
        print("=" * 60)
        print("✓ R2D2 CHATBOT READY")
        print("=" * 60)

    def _init_components(self):
        """Initialize all components"""

        # 1. Wake Word (optional)
        if self.config.USE_WAKE_WORD:
            self.wake_word = WakeWordListener()
            print(f"✓ Wake word: {self.wake_word.wake_word_name}")
        else:
            self.wake_word = None

        # 2. VAD Recorder
        self.vad_recorder = VADRecorder(
            sample_rate=16000,
            aggressiveness=self.config.VAD_AGGRESSIVENESS,
            speech_frames_threshold=self.config.VAD_SPEECH_THRESHOLD,
            min_recording_duration=self.config.VAD_MIN_DURATION
        )
        print("✓ VAD Recorder initialized (filters typing/falling sounds)")

        # 3. STT (Whisper)
        self.stt = WhisperSTT(
            model_size=self.config.WHISPER_MODEL,
            device=self.config.WHISPER_DEVICE,
            compute_type=self.config.WHISPER_COMPUTE_TYPE
        )

        # 4. LLM (Groq)
        self.llm = GroqClient(
            api_key=self.config.GROQ_API_KEY,
            model=self.config.LLM_MODEL
        )
        print(f"✓ LLM: {self.config.LLM_MODEL}")

        # 5. TTS Components
        self.r2d2 = R2D2WordVocabulary()
        self.piper = PiperTTS(default_voice=self.config.TTS_VOICE)

        # Display voice info
        voice_name = "en_US-ljspeech-high" if self.config.TTS_VOICE == 'female' else "en_GB-alan-medium"
        print(f"✓ TTS: Hybrid Bumblebee-style (R2D2 + Piper {self.config.TTS_VOICE})")
        print(f"  Voice: {voice_name} | Effect: {self.config.TTS_EFFECT}")

    def wait_for_wake_word(self):
        """Wait for wake word detection (blocking)"""
        if not self.wake_word:
            return

        try:
            self.wake_word.start(
                callback=None,
                sensitivity=0.5,
                stop_on_detect=True
            )
        except Exception as e:
            print(f"Wake word error: {e}")

        time.sleep(0.3)  # Let audio device release
        print(f"✓ Wake up!")
        self.is_awake = True

    def should_go_to_sleep(self, text):
        """Check if user wants to go to sleep"""
        sleep_phrases = [
            'goodbye', 'good bye', 'bye', 'go to sleep',
            'sleep mode', 'stop listening', 'that\'s all',
            'thanks olaf', 'thank you olaf', 'see you later'
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in sleep_phrases)

    def play_acknowledgment(self, emotion='curious'):
        """Play R2D2 acknowledgment"""
        print(f"[R2D2 {emotion} beep]")
        ack_audio = self.r2d2.speak_sentence("thinking", emotion=emotion)
        sd.play(ack_audio, self.r2d2.params.sample_rate)
        sd.wait()

    def listen_with_vad(self):
        """Record audio with VAD"""
        print("\n--- Listening for your command ---")
        audio = self.vad_recorder.record_with_vad(max_duration=30)
        return audio

    def transcribe(self, audio):
        """Transcribe audio to text (English only)"""
        if len(audio) == 0:
            return ""

        print("--- Transcribing (English) ---")
        result = self.stt.transcribe(audio, sample_rate=16000, language='en')
        return result['text']

    def get_llm_response(self, user_text):
        """Get response from LLM"""
        print("--- Processing with LLM ---")
        return self.llm.get_response(user_text)

    def speak_response(self, response_dict):
        """
        Speak response with Bumblebee-style hybrid TTS

        Args:
            response_dict: Dictionary with 'r2d2_message' and 'info_message' keys
        """
        print(f"--- Responding (Bumblebee Style) ---")

        r2d2_message = response_dict.get('r2d2_message', '')
        info_message = response_dict.get('info_message', None)

        # Step 1: Play R2D2 primary response
        if r2d2_message:
            print(f"[R2D2 curious: \"{r2d2_message}\"]")
            r2d2_audio = self.r2d2.speak_sentence(r2d2_message, emotion='curious')
            sd.play(r2d2_audio, self.r2d2.params.sample_rate)
            sd.wait()

        # Step 2: If there's specific information, use transmission mode
        if info_message:
            # Brief transition ping
            print("[R2D2 transition ping]")
            transition = self.r2d2.ping(duration=0.08)
            sd.play(transition, self.r2d2.params.sample_rate)
            sd.wait()
            time.sleep(0.1)

            # Transmit specific information with effect
            print(f"[TRANSMISSION: \"{info_message}\"]")
            self.piper.speak(info_message, voice=self.config.TTS_VOICE, effect=self.config.TTS_EFFECT)

            # R2D2 confirmation
            print("[R2D2 affirmative confirmation]")
            confirm = self.r2d2.speak_sentence("understood", emotion='happy')
            sd.play(confirm, self.r2d2.params.sample_rate)
            sd.wait()

        # Delay after speaking to avoid echo pickup
        time.sleep(0.5)

    def run_conversation_turn(self):
        """Run one conversation turn"""

        # 1. Listen with VAD
        audio = self.listen_with_vad()

        if len(audio) == 0:
            print("⚠ No valid audio captured (too short or no speech)")
            return 'retry'

        # 2. Transcribe
        user_text = self.transcribe(audio)

        if not user_text:
            print("⚠ Could not transcribe speech")
            return 'retry'

        print(f"\nUser: \"{user_text}\"")

        # 3. Check if user wants to go to sleep
        if self.should_go_to_sleep(user_text):
            print("💤 Going to sleep mode...")
            self.is_awake = False

            goodbye_response = {
                'r2d2_message': 'sleep mode',
                'info_message': 'Say my wake word to activate'
            }
            print(f"R2D2 Chatbot: Going to sleep")
            self.speak_response(goodbye_response)

            return 'sleep'

        # 4. Get LLM response
        response_dict = self.get_llm_response(user_text)

        # Display response
        print(f"R2D2: \"{response_dict['r2d2_message']}\"")
        if response_dict['info_message']:
            print(f"TRANSMISSION: \"{response_dict['info_message']}\"")

        # 5. Speak response
        self.speak_response(response_dict)

        return True

    def run(self):
        """Main run loop with continuous conversation"""
        print()
        print("🚀 R2D2 Chatbot Started")
        print()
        print("💡 How to use:")
        print("  - Say wake word to activate")
        print("  - Have as many conversations as you want")
        print("  - Say 'goodbye' or 'go to sleep' when done")
        print("  - Press Ctrl+C to exit")
        print()

        try:
            while True:
                # Wait for wake word if not awake
                if not self.is_awake:
                    if self.config.USE_WAKE_WORD:
                        self.wait_for_wake_word()
                        self.play_acknowledgment('happy')
                    else:
                        input("\n[Press Enter to start...]")
                        self.is_awake = True

                # Continuous conversation loop while awake
                while self.is_awake:
                    print("\n" + "="*60)
                    result = self.run_conversation_turn()

                    if result == 'sleep':
                        break
                    elif result == 'retry':
                        continue
                    elif result:
                        print("\n✓ Ready for next question...")
                        print("💬 Just start speaking, or say 'goodbye' to sleep")
                    else:
                        print("\n⚠ Error occurred, try again...")

        except KeyboardInterrupt:
            print("\n\n✓ R2D2 Chatbot stopped")
