# jarvis_fixed.py
import os
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pywhatkit
import webbrowser
import openai     # keep for backward compat if needed
from openai import OpenAI

# --- IMPORTANT: set OPENAI_API_KEY as an environment variable, don't hardcode ---
# Windows (cmd, one-time for session): set OPENAI_API_KEY=sk-...
# Windows (PowerShell): $env:OPENAI_API_KEY="sk-..."
# Permanently (Windows): setx OPENAI_API_KEY "sk-..."
# Or put in a .env and use python-dotenv to load it.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set. See comments in file.")

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        print("Recognizing...")
        command = r.recognize_google(audio).lower()
        print(f"User: {command}")
    except sr.UnknownValueError:
        print("Could not understand. Please say that again.")
        return ""
    except sr.RequestError:
        print("Could not request results. Check your internet connection.")
        return ""
    return command

def chat_with_gpt(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7
        )
        # Access the assistant response text:
        return completion.choices[0].message.content.strip()
    except Exception as e:
        # Print/log full exception to diagnose; return a friendly message as well.
        print("OpenAI error:", repr(e))
        return "Sorry — I couldn't reach the language model. Check the API key, network, or quota."

def execute_command(command):
    if "hello" in command:
        speak("Hello! How can I assist you?")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
    elif "date" in command:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today}")
    elif "search wikipedia" in command:
        speak("What do you want to search on Wikipedia?")
        query = take_command()
        if query:
            try:
                results = wikipedia.summary(query, sentences=2)
                speak(results)
            except Exception as e:
                speak("I couldn't find that on Wikipedia.")
                print("Wikipedia error:", e)
    elif "play" in command:
        song = command.replace("play", "").strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")
    elif "chat" in command or "ask" in command:
        speak("What would you like to ask ChatGPT?")
        user_input = take_command()
        if user_input:
            response = chat_with_gpt(user_input)
            print("ChatGPT:", response)
            speak(response)
    elif "quit" in command or "exit" in command:
        speak("Goodbye!")
        exit()
    else:
        speak("I'm not sure how to help with that. Let me try to find an answer.")
        response = chat_with_gpt(command)
        print("ChatGPT:", response)
        speak(response)

if __name__ == "__main__":
    speak("Hello! I am Jarvis, your personal assistant. How can I help you?")
    while True:
        cmd = take_command()
        if cmd:
            execute_command(cmd)
