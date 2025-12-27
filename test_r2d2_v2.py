from r2d2_voice import R2D2Voice

voice = R2D2Voice()

  # Your example!
audio = voice.speak_text("I am good", emotion='happy')
voice.save(emotion='happy', filepath='test.wav')  # Save to listen