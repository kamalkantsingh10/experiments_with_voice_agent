#!/usr/bin/env python3
"""
Hybrid Voice System Demo
Combines R2D2 acknowledgment sounds with Piper TTS responses
"""

from r2d2_word_vocabulary import R2D2WordVocabulary
from piper_tts import PiperTTS
import numpy as np
import sounddevice as sd


class HybridVoiceAgent:
    """
    Voice agent that uses R2D2 for acknowledgments and Piper for intelligible responses
    """

    def __init__(self, tts_voice='female'):
        """
        Initialize hybrid voice agent

        Args:
            tts_voice: 'male' or 'female' for Piper TTS
        """
        print("Initializing Hybrid Voice Agent...")
        self.r2d2 = R2D2WordVocabulary()
        self.tts = PiperTTS(default_voice=tts_voice)
        print("✓ Hybrid Voice Agent ready!")
        print()

    def acknowledge(self, emotion='curious'):
        """
        Play R2D2 acknowledgment sound (instant feedback)

        Args:
            emotion: R2D2 emotion for acknowledgment
        """
        # Short acknowledgment phrase
        ack_audio = self.r2d2.speak_sentence("thinking", emotion=emotion)
        sd.play(ack_audio, self.r2d2.params.sample_rate)
        sd.wait()

    def respond(self, text, voice=None, effect='comlink', acknowledge_emotion='curious'):
        """
        Full response: R2D2 acknowledgment + Piper TTS

        Args:
            text: Response text to speak
            voice: 'male' or 'female' (uses default if not specified)
            effect: Audio effect - 'clear', 'radio', 'comlink', or 'hologram'
            acknowledge_emotion: R2D2 emotion for acknowledgment
        """
        # Step 1: Instant R2D2 acknowledgment
        print(f"[R2D2 {acknowledge_emotion} beep]")
        self.acknowledge(acknowledge_emotion)

        # Step 2: Generate and play Piper response
        print(f"[Piper TTS: \"{text}\"]")
        self.tts.speak(text, voice=voice, effect=effect)

    def quick_response(self, text, emotion='happy'):
        """
        Quick R2D2-only response (no TTS, just emotive sounds)

        Args:
            text: Text to represent as R2D2 sounds
            emotion: R2D2 emotion
        """
        print(f"[R2D2 {emotion}: \"{text}\"]")
        audio = self.r2d2.speak_sentence(text, emotion=emotion)
        sd.play(audio, self.r2d2.params.sample_rate)
        sd.wait()


# Demo
if __name__ == "__main__":
    print("=" * 60)
    print("OLAF VOICE AGENT - STAR WARS STYLE DEMO")
    print("20 Scenarios for Daily Tasks")
    print("=" * 60)
    print()

    # Initialize agent
    agent = HybridVoiceAgent(tts_voice='female')

    scenarios = [
        # Weather & Environment
        ("What's the weather?", "Atmospheric conditions stable, 22 degrees celsius, no hostile weather detected.", 'comlink', 'curious'),
        ("Is it going to rain?", "Negative commander, sensors show clear skies for the next rotation.", 'comlink', 'neutral'),

        # Time & Scheduling
        ("What time is it?", "Current time is fourteen hundred hours, galactic standard.", 'comlink', 'neutral'),
        ("Set alarm for 7am", "Wake-up protocol initiated for oh seven hundred hours, affirmative.", 'comlink', 'happy'),
        ("Do I have any meetings?", "Affirmative, council briefing scheduled at fifteen hundred hours.", 'comlink', 'curious'),

        # Smart Home Control
        ("Turn on the lights", "Illumination systems activated, bay area now operational.", 'comlink', 'neutral'),
        ("Lock the doors", "Security protocols engaged, all entry points sealed.", 'comlink', 'neutral'),
        ("Set temperature to 21", "Environmental controls adjusted, climate stabilizing at 21 degrees.", 'comlink', 'neutral'),

        # Information & Search
        ("What's the news?", "Incoming transmission from the outer rim, reviewing latest intelligence reports.", 'hologram', 'curious'),
        ("How do I fix my speeder?", "Accessing repair protocols from the technical database, standby.", 'comlink', 'curious'),

        # Reminders & Tasks
        ("Remind me to call mom", "Communication reminder logged, I will alert you at the designated time.", 'comlink', 'happy'),
        ("What's on my todo list?", "Three mission objectives pending, shall I relay the details commander?", 'comlink', 'curious'),

        # Navigation & Travel
        ("How long to get to work?", "Current route analysis shows 23 minutes via the hyperspace lane.", 'comlink', 'neutral'),
        ("Traffic update please", "Multiple transport vessels detected, recommend alternative corridor.", 'comlink', 'curious'),

        # Entertainment & Media
        ("Play my music", "Accessing your cantina music collection, preparing playback systems.", 'comlink', 'happy'),
        ("Pause the video", "Media transmission suspended, standing by for your command.", 'comlink', 'neutral'),

        # Emergency & Alerts
        ("Is everything okay?", "All systems nominal, no threats detected in the perimeter.", 'comlink', 'happy'),
        ("Alert me if temperature drops", "Thermal monitoring protocol activated, you will be notified of any anomalies.", 'comlink', 'neutral'),

        # Shopping & Lists
        ("Add bread to shopping list", "Supply requisition updated, bread added to cargo manifest.", 'comlink', 'neutral'),
        ("What's on my shopping list?", "Current provisions list contains five items, ready for the supply run.", 'comlink', 'curious'),
    ]

    for i, (user_input, response, effect, emotion) in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}/{len(scenarios)} ---")
        print(f"User: '{user_input}'")
        agent.respond(response, effect=effect, acknowledge_emotion=emotion)

        # Add small pause between scenarios for better listening experience
        import time
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("OLAF Demo Complete!")
    print()
    print("Demonstrated capabilities:")
    print("  ✓ Weather & environment monitoring")
    print("  ✓ Time management & scheduling")
    print("  ✓ Smart home control")
    print("  ✓ Information retrieval")
    print("  ✓ Reminders & task management")
    print("  ✓ Navigation & traffic")
    print("  ✓ Entertainment control")
    print("  ✓ Security & alerts")
    print("  ✓ Shopping & lists")
    print()
    print("Voice modes used:")
    print("  • Comlink effect for standard communications")
    print("  • Hologram effect for information transmissions")
    print("  • R2D2 emotions: curious, neutral, happy")
    print("=" * 60)
