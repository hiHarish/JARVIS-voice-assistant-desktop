import time
import threading
import datetime
import json
import os
import pyttsx3

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)

REMINDERS_FILE = "reminders.json"

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def save_reminders(reminders):
    """Save reminders to a JSON file."""
    with open(REMINDERS_FILE, "w") as file:
        json.dump(reminders, file)

def load_reminders():
    """Load reminders from a JSON file."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as file:
            return json.load(file)
    return []

def add_reminder(task, remind_time):
    """Add a new reminder."""
    reminders = load_reminders()
    reminders.append({"task": task, "time": remind_time})
    save_reminders(reminders)
    speak(f"Reminder set for {task} at {remind_time}")
    print(f"Reminder set: {task} at {remind_time}")

def list_reminders():
    """List all upcoming reminders."""
    reminders = load_reminders()
    if reminders:
        speak("Here are your reminders:")
        for reminder in reminders:
            print(f"{reminder['task']} at {reminder['time']}")
            speak(f"{reminder['task']} at {reminder['time']}")
    else:
        speak("You have no upcoming reminders.")
        print("No reminders found.")

def check_reminders():
    """Continuously check for reminders and notify when due."""
    while True:
        reminders = load_reminders()
        current_time = datetime.datetime.now().strftime("%H:%M")
        for reminder in reminders:
            if reminder["time"] == current_time:
                speak(f"Reminder: {reminder['task']}")
                print(f"Reminder Alert: {reminder['task']}")
                reminders.remove(reminder)  # Remove completed reminder
                save_reminders(reminders)
        time.sleep(60)  # Check every minute

