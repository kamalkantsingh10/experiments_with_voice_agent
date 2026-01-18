#!/usr/bin/env python3
"""
Full-Featured R2D2 Chatbot Example (Bumblebee-Style)

Shows custom configuration options:
- Different voices (male/female)
- Audio effects (clear_transmission, comlink, radio, hologram, dramatic)
- VAD settings (noise filtering)
- Wake word enable/disable
"""

from r2d2_chatbot.agent import R2D2ChatbotAgent
from r2d2_chatbot.config import Config


def example_custom_voice():
    """Example: Using male voice with comlink effect"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Male Voice with Comlink Effect")
    print("=" * 60)
    
    config = Config()
    config.TTS_VOICE = 'male'  # British male voice
    config.TTS_EFFECT = 'comlink'  # Star Wars comlink effect
    
    agent = R2D2ChatbotAgent(config=config)
    agent.run()


def example_no_wake_word():
    """Example: Without wake word (press Enter to start)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: No Wake Word (Press Enter Mode)")
    print("=" * 60)
    
    config = Config()
    config.USE_WAKE_WORD = False  # Disable wake word
    
    agent = R2D2ChatbotAgent(config=config)
    agent.run()


def example_noisy_environment():
    """Example: Settings for noisy environment (more aggressive filtering)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Noisy Environment Settings")
    print("=" * 60)
    print("Filters typing, background noise, objects falling")
    
    config = Config()
    config.VAD_AGGRESSIVENESS = 3  # Maximum filtering
    config.VAD_SPEECH_THRESHOLD = 12  # More frames needed to start
    config.VAD_MIN_DURATION = 2.0  # Longer minimum duration
    
    agent = R2D2ChatbotAgent(config=config)
    agent.run()


def example_quiet_environment():
    """Example: Settings for quiet environment (more sensitive)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Quiet Environment Settings")
    print("=" * 60)
    print("More sensitive to pick up speech easily")
    
    config = Config()
    config.VAD_AGGRESSIVENESS = 1  # Less aggressive
    config.VAD_SPEECH_THRESHOLD = 5  # Fewer frames needed
    config.VAD_MIN_DURATION = 1.0  # Shorter minimum
    
    agent = R2D2ChatbotAgent(config=config)
    agent.run()


def example_different_effects():
    """Example: Trying different audio effects"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Different Audio Effects Demo")
    print("=" * 60)
    print("Available effects:")
    print("  - clear_transmission (RECOMMENDED)")
    print("  - comlink (Star Wars radio)")
    print("  - radio (Vintage radio)")
    print("  - hologram (Glitchy hologram)")
    print("  - dramatic (Deep narrator)")
    print("  - clear (No effect)")
    print()
    
    effect = input("Choose effect (or press Enter for clear_transmission): ").strip()
    if not effect:
        effect = 'clear_transmission'
    
    config = Config()
    config.TTS_EFFECT = effect
    
    agent = R2D2ChatbotAgent(config=config)
    agent.run()


def main():
    """Main menu to choose example"""
    print("=" * 60)
    print("R2D2 CHATBOT - BUMBLEBEE-STYLE EXAMPLES")
    print("=" * 60)
    print()
    print("Choose an example:")
    print()
    print("1. Male voice with comlink effect")
    print("2. No wake word (press Enter mode)")
    print("3. Noisy environment (aggressive filtering)")
    print("4. Quiet environment (more sensitive)")
    print("5. Try different audio effects")
    print("6. Default settings (female voice, clear_transmission)")
    print()
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == '1':
        example_custom_voice()
    elif choice == '2':
        example_no_wake_word()
    elif choice == '3':
        example_noisy_environment()
    elif choice == '4':
        example_quiet_environment()
    elif choice == '5':
        example_different_effects()
    elif choice == '6':
        print("\nUsing default settings...")
        agent = R2D2ChatbotAgent()
        agent.run()
    else:
        print("Invalid choice. Using default settings...")
        agent = R2D2ChatbotAgent()
        agent.run()


if __name__ == "__main__":
    main()
