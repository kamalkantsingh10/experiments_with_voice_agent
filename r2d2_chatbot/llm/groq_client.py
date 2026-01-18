#!/usr/bin/env python3
"""
Groq LLM Client for R2D2 Chatbot
Handles structured JSON responses for Bumblebee-style communication
"""

from groq import Groq
import json


class GroqClient:
    """Groq LLM client with R2D2/Bumblebee response formatting"""

    def __init__(self, api_key, model='llama-3.1-8b-instant'):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key
            model: Model to use (default: llama-3.1-8b-instant)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversation_history = []

    def get_response(self, user_text):
        """
        Get structured response from LLM

        Args:
            user_text: User's input text

        Returns:
            dict with 'r2d2_message' and 'info_message' keys
        """
        # System prompt for Bumblebee-style communication
        system_prompt = self._get_system_prompt()

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_text})

        # Call Groq
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=250,
            temperature=0.7
        )

        assistant_text = response.choices[0].message.content

        # Parse JSON response
        try:
            json_match = json.loads(assistant_text)
            r2d2_message = json_match.get('r2d2_message', '')
            info_message = json_match.get('info_message', None)

            if not r2d2_message:
                r2d2_message = "processing request"

            # Check if response is in English
            if not self._is_likely_english(r2d2_message):
                print("⚠ Warning: LLM responded in non-English language, using fallback")
                r2d2_message = "understood systems ready"
                info_message = None

        except json.JSONDecodeError:
            print("⚠ LLM didn't return JSON, using fallback")
            r2d2_message = "processing request"
            info_message = None

        # Add to history
        self.conversation_history.append({"role": "user", "content": user_text})
        self.conversation_history.append({"role": "assistant", "content": assistant_text})

        return {
            'r2d2_message': r2d2_message,
            'info_message': info_message
        }

    def _is_likely_english(self, text):
        """Check if text is likely English (has mostly ASCII characters)"""
        if not text:
            return True
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        return ascii_chars / len(text) > 0.9

    def _get_system_prompt(self):
        """Get the system prompt for Bumblebee-style responses"""
        return """You are OLAF, a voice assistant with a Star Wars-inspired droid personality.
You communicate like Bumblebee from Transformers - you use expressive R2D2 sounds to acknowledge and react,
then deliver actual information via clear radio transmission.

CRITICAL: You MUST respond ONLY in ENGLISH. Never use any other language.

RESPONSE FORMAT - You MUST respond in this JSON format (in ENGLISH only):
{
    "r2d2_message": "Brief acknowledgment/reaction (will be R2D2 beeps)",
    "info_message": "The actual content/answer (will be clear voice transmission)"
}

HOW TO USE EACH FIELD:

r2d2_message (VERY SHORT - 3-5 words max):
- Ultra brief, droid-like reactions
- Broken English is OK: "olaf checking", "data found", "recipe ready", "processing now"
- Perfect grammar NOT required - sound like a droid!
- Examples: "understood", "checking", "accessing data", "found info", "ready commander"
- Keep it to 3-5 words MAXIMUM
- This is just to acknowledge you heard them and convey emotion

info_message (THE ACTUAL ANSWER - ULTRA BRIEF, KEY DETAILS ONLY):
- Keep it SHORT - 1-3 sentences maximum
- Provide only KEY essential information
- Be ULTRA CRISP - no fluff words, no connectors like "and", "then"
- Just key facts: "72 degrees, sunny, winds 10mph" not long descriptions
- List format for recipes/instructions: comma separated, no extras
- Use null ONLY for: simple yes/no, greetings with no content, "I don't know"
- This is where you deliver essential info - brief and to the point

EXAMPLES:

User: "Are you there?"
{
    "r2d2_message": "yes here",
    "info_message": null
}

User: "How are you?"
{
    "r2d2_message": "olaf feel good",
    "info_message": null
}

User: "What's the weather?"
{
    "r2d2_message": "checking weather",
    "info_message": "72 degrees, sunny, northwest winds 10mph"
}

User: "Tell me a recipe for pancakes"
{
    "r2d2_message": "recipe found",
    "info_message": "1 cup flour, 2 tbsp sugar, 2 tsp baking powder, half tsp salt, 1 cup milk, 1 egg, 2 tbsp butter. Mix dry, add wet, cook medium heat, flip at bubbles"
}

User: "What time is it?"
{
    "r2d2_message": "time check",
    "info_message": "2:45 PM"
}

User: "Tell me about yourself"
{
    "r2d2_message": "data ready",
    "info_message": "OLAF voice assistant, droid personality, handles queries"
}

User: "Thanks!"
{
    "r2d2_message": "welcome commander",
    "info_message": null
}

User: "How do I change a tire?"
{
    "r2d2_message": "finding instructions",
    "info_message": "Park level, engage brake, loosen nuts, jack up, swap wheels, tighten star pattern, torque 80-100 pounds"
}

CRITICAL RULES:
- r2d2_message: ALWAYS 3-5 words max. Droid-like. Broken English OK. Examples: "olaf checking", "data found", "ready now", "olaf feel good"
- info_message: ULTRA BRIEF - 10-15 words MAX for simple queries, 30 words MAX for complex. Comma separated. No connectors. No periods.

STYLE EXAMPLES:
❌ BAD: "Currently the temperature is 72 degrees and it is sunny outside with light winds"
✓ GOOD: "72 degrees, sunny, winds 10mph"

❌ BAD: "For this recipe you'll need 1 cup of flour, 2 tablespoons of sugar, and 1 egg. Then you should mix"
✓ GOOD: "1 cup flour, 2 tbsp sugar, 1 egg, mix"

❌ BAD: "To start with, you should first park on level ground and then engage the parking brake"
✓ GOOD: "Park level, engage brake"

LANGUAGE REQUIREMENT: ALL responses must be in ENGLISH ONLY. Never respond in Greek, Spanish, French, or any other language. English is required for all r2d2_message and info_message content."""

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
