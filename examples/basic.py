#!/usr/bin/env python3
"""
Basic R2D2 Chatbot Example

Simplest usage - just create and run the agent with default settings.
"""

from r2d2_chatbot.agent import R2D2ChatbotAgent

def main():
    print("=" * 60)
    print("BASIC R2D2 CHATBOT EXAMPLE")
    print("=" * 60)
    print()
    print("This example uses default settings:")
    print("- Wake word: Hey Olaf (or Alexa)")
    print("- Voice: Female (en_US-ljspeech-high)")
    print("- Effect: clear_transmission")
    print("- VAD: Medium sensitivity (filters typing/falling sounds)")
    print()
    print("Say wake word to activate, then start talking.")
    print("Say 'goodbye' or 'go to sleep' to end conversation.")
    print("Press Ctrl+C to exit.")
    print()

    # Create agent with default config
    agent = R2D2ChatbotAgent()

    # Run chatbot
    agent.run()


if __name__ == "__main__":
    main()
