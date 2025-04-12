import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import wikipedia
import webbrowser
import os
import requests
import psutil
import pywhatkit
import datetime
import time
import re
from AppOpener import open,close
import json 
import threading
import reminders


# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture voice input and convert to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("No speech detected.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
            speak("Sorry, I couldn't understand. Please repeat.")
        except sr.RequestError:
            print("Speech Recognition service error.")
            speak("There is an issue with the speech recognition service.")

def listen_wakeword():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("No wake word.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech Recognition service error.")
            speak("There is an issue with the speech recognition service.")

genai.configure(api_key="TOUR_GEMINI_API_KEY")           
chat_history = [
    {"role": "user", "parts": [{"text": "You are a helpful AI assistant. Keep responses short and conversational."}]}
]

def clean_response(response_text):
    """Removes symbols, bullet points, and markdown-like formatting from AI response."""
    response_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", response_text)  # Remove **bold text**
    response_text = re.sub(r"\*(.*?)\*", r"\1", response_text)  # Remove *italic text*
    response_text = re.sub(r"[\*\-\•]\s*", "", response_text)  # Remove bullet points
    response_text = re.sub(r"[\n]+", " ", response_text)  # Convert new lines to spaces
    response_text = re.sub(r"[^\w\s.,!?]", "", response_text)  # Remove special symbols
    return response_text.strip()
def ask_gemini(prompt):
    """Generates a conversational AI response using Gemini API while maintaining context."""
    try:
        # Append user query to chat history
        chat_history.append({"role": "user", "parts": [{"text": prompt}]})

        # Send conversation history to Gemini API
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(chat_history)

        # Extract AI response
        ai_response = response.text.strip() if response and response.text else "I didn't get that. Can you clarify?"

        # Clean the response to remove symbols and formatting
        ai_response = clean_response(ai_response)

        # Append AI response to chat history
        chat_history.append({"role": "model", "parts": [{"text": ai_response}]})

        return ai_response
    except Exception as e:
        return f"Error: {str(e)}"

def open_application(app_name):
    """Open applications based on commands."""
    app_name= app_name.capitalize()
    try:
        print(app_name)
        open(app_name, match_closest=True)  # Try opening the application
        time.sleep(2)  # Wait for a moment to check if it launches
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def close_application(app_name):

    app_name= app_name.capitalize()
    try:
        print(app_name)
        close(app_name, match_closest=True, output=False)
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def control_system(command):
    """Perform system control tasks."""
    if "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down the system."
    elif "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting the system."
    elif "battery" in command:
        battery = psutil.sensors_battery()
        return f"Battery level is {battery.percent}%."
    else:
        return "Command not recognized for system control."

def play_youtube_video(query):
    """Play YouTube videos using pywhatkit."""
    pywhatkit.playonyt(query)
    return f"Playing {query} on YouTube."


def convert_to_24_hour(time_str):
    """
    Converts time from 12-hour format (e.g., "5:30 PM") to 24-hour format ("17:30").
    """
    try:
        if  "a.m."  or "p.m." in time_str:
            time_str1= time_str.replace("a.m.","AM").replace("p.m.","PM")
            time_obj = datetime.datetime.strptime(time_str1, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        else:
            return datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        return None


def execute_command(command):
    """Process and execute user commands."""
    if "open" in command:
        app_name = command.replace("open", "").strip()
        response = open_application(app_name)
    elif "close" in command:
        app_name = command.replace("close","").strip()
        response = close_application(app_name)
    elif "set reminder" in command or "add reminder" in command or "remind me" in command:
        time_pattern = re.search(r'(\d{1,2}[:.]\d{2} ?(?:a.m.|p.m.)?)|(\d{1,2} ?(?:a.m.|p.m.))', command)
        print(time_pattern)
        if time_pattern:
            raw_time = time_pattern.group()  # Extract the time part
            reminder_text = command.replace("set reminder to", "").replace(raw_time, "").replace("at", "").strip()

            # Convert 12-hour format to 24-hour format if needed
            reminder_time = convert_to_24_hour(raw_time)
            print(reminder_text)
            print(reminder_time)
            reminders.add_reminder(reminder_text, reminder_time)
        else:
            speak("At what time?")
            time1=listen()
            reminder_time1 = convert_to_24_hour(time1)
            reminders.add_reminder(command, reminder_time1)
        response="Done!"
    elif "list reminders"in command or "show reminder" in command or "show all reminders"  in command:
        reminders.list_reminders()
        response = "Listed your reminders."
    elif "search" in command:
        query = command.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        response = f"Searching Google for {query}."
    elif "play" in command:
        query = command.replace("play", "").strip()
        response = play_youtube_video(query)
    elif "shutdown" in command or "restart" in command or "battery" in command:
        response = control_system(command)
    elif "time" in command:
        response = f"The current time is {datetime.datetime.now().strftime('%H:%M')}"
    elif "exit" in command or "bye" in command:
        speak("Goodbye!")
        exit()
    else:
        response = ask_gemini(command)

    print("Assistant:", response)
    speak(response)
# Main loop
if __name__ == "__main__":
    while True:
        reminder_thread = threading.Thread(target=reminders.check_reminders, daemon=True)
        reminder_thread.start()
        user_command = listen_wakeword()
        if user_command:
            wake_word = user_command.lower()
            if wake_word == "hey jarvis":
                speak("yes?")
                user_command1= listen()
                if user_command1:
                    user_command1= user_command1.lower()
                    execute_command(user_command1)
                else:
                    speak("Sorry! I didn't catch that")
            elif "hey jarvis" in wake_word:
                print("k")
                command = wake_word.replace("hey jarvis","").strip()
                execute_command(command)
            else:
                print("no wake word detected")
        else:
            user_command = listen_wakeword()
