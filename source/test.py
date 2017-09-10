import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    engine.setProperty('voice',voice.id)
    engine.say('Assignment added successfully')
    engine.runAndWait()
