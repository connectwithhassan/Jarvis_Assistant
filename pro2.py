import customtkinter as ctk
import pyttsx3
import datetime
import wikipedia
import webbrowser
import speech_recognition as sr
import threading
import requests
import csv
import random
import logging
import os

# 🧠 Initialize TTS Engine
engine = pyttsx3.init()
engine.setProperty('volume', 0.7)

# 🔀 Custom responses memory
custom_responses = {}

# 😊 Casual chat responses
casual_responses = {
    "how are you": "Main theek hoon, aap kaise ho?",
    "what's up": "Sab badhiya hai! Aap sunao?",
    "who are you": "Main Jarvis hoon, aapka AI assistant.",
    "hello": "Hello! Kaise ho?",
    "hi": "Hi there!",
    "thank you": "Aapka swagat hai!",
    "thanks": "Koi baat nahi!",
    "good night": "Shubh ratri! Accha soyiye."
}

def speak(text):
    engine.say(text)
    engine.runAndWait()

# 🶕️ Greet user with time and wishes
def speak_greeting():
    now = datetime.datetime.now()
    hour = now.hour
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%B %d, %Y")

    if 5 <= hour < 12:
        greet = "Good Morning!"
    elif 12 <= hour < 17:
        greet = "Good Afternoon!"
    else:
        greet = "Good Evening!"


    msg = f"{greet} Aaj ki tareekh hai {date_str}, aur waqt hai {time_str}."
    display_response(f"Jarvis: {msg}", "jarvis")
    speak(msg)

# 🌦️ Weather Feature
def get_weather(city):
    api_key = "your_openweathermap_api_key"
    if api_key == "your_openweathermap_api_key":
        return "Weather feature not active. Please add your API key."
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            return f"{city} ka temperature {temp}°C hai with {desc}."
        else:
            return "City not found."
    except Exception as e:
        logging.error(f"Weather Error: {e}")
        return "Weather fetch failed."

# 😂 Joke Reader
def tell_joke():
    try:
        with open("jokes.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            jokes = [row["joke"] for row in reader if row["joke"].strip()]
            if jokes:
                return random.choice(jokes)
            else:
                return "Mujhe koi joke nahi mila."
    except Exception as e:
        logging.error(f"Joke Error: {e}")
        return "Jokes file load nahi ho saki."

# 🎵 Music Player
def play_music():
    music_folder = "music"
    try:
        songs = [song for song in os.listdir(music_folder) if song.endswith(".mp3")]
        if songs:
            song_path = os.path.join(music_folder, random.choice(songs))
            os.startfile(song_path)
            return "Music play kar raha hoon."
        else:
            return "Music folder mein koi gana nahi mila."
    except Exception as e:
        logging.error(f"Music Error: {e}")
        return "Music play karne mein dikkat ho gayi."

# 🧠 Handle custom response teaching
def handle_custom_teach(query):
    if "remember that when i say" in query and "you say" in query:
        try:
            trigger_part = query.split("remember that when i say", 1)[1].strip()
            trigger, response = trigger_part.split("you say", 1)
            trigger = trigger.strip().strip('"')
            response = response.strip().strip('"')
            custom_responses[trigger.lower()] = response
            return f"Okay, I will respond to '{trigger}' with '{response}'."
        except Exception as e:
            logging.error(f"Custom Teach Error: {e}")
            return "Sorry, mujhe wo custom response samajh nahi aaya."
    return None

# 🔍 Command Processor
def process_command(query):
    global app
    query = query.lower().strip()

    taught = handle_custom_teach(query)
    if taught:
        return taught

    if query in custom_responses:
        return custom_responses[query]

    for key in casual_responses:
        if key in query:
            return casual_responses[key]

    if "time" in query:
        return f"Abhi ka time hai {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in query:
        return f"Aaj ki date hai {datetime.datetime.now().strftime('%B %d, %Y')}"
    elif "who is" in query:
        person = query.replace("who is", "").strip()
        try:
            return wikipedia.summary(person, sentences=2)
        except:
            return "Wikipedia se info nahi mil saki."
    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
        return "YouTube khol raha hoon..."
    elif "search" in query:
        term = query.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={term}")
        return f"Google pe {term} search kar raha hoon..."
    elif "weather" in query:
        if "in" in query:
            city = query.split("in")[-1].strip()
        else:
            city = "Karachi"
        return get_weather(city)
    elif "joke" in query:
        return tell_joke()
    elif "play music" in query or "play some music" in query:
        return play_music()
    elif "exit" in query or "bye" in query:
        speak("Goodbye!")
        app.destroy()
        return "App band ki ja rahi hai..."
    else:
        return "Sorry, mujhe ye samajh nahi aaya."

# 🎧 Continuous Listening
def continuous_listener():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            try:
                status_label.configure(text="Listening...", text_color="green")
                audio = recognizer.listen(source, timeout=5)
                status_label.configure(text="Processing...", text_color="yellow")
                query = recognizer.recognize_google(audio)
                display_response(f"You: {query}", "user")
                response = process_command(query)
                display_response(f"Jarvis: {response}", "jarvis")
                speak(response)
                status_label.configure(text="Idle", text_color="white")
            except:
                status_label.configure(text="Idle", text_color="white")
                continue

# 💬 Show messages
def display_response(message, sender="jarvis"):
    prefix = "🤖 " if sender == "jarvis" else "🕵️ "
    chat_log.insert(ctk.END, prefix + message + "\n")
    chat_log.see(ctk.END)

# ⏰ Update Clock
def update_clock():
    clock_label.configure(text=datetime.datetime.now().strftime("%I:%M:%S %p"))
    app.after(1000, update_clock)

# 🌙 CustomTkinter GUI Setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Jarvis AI Dashboard")
app.geometry("720x850")

frame = ctk.CTkFrame(app, corner_radius=25)
frame.pack(pady=30, padx=30, fill="both", expand=True)

# Aesthetic Fonts
title_label = ctk.CTkLabel(frame, text="🤖 Jarvis AI Assistant", font=("Poppins", 30, "bold"))
title_label.pack(pady=(20, 10))

clock_label = ctk.CTkLabel(frame, text="", font=("Poppins", 18))
clock_label.pack()

status_label = ctk.CTkLabel(frame, text="Idle", font=("Poppins", 16), text_color="white")
status_label.pack(pady=5)

chat_log = ctk.CTkTextbox(frame, width=650, height=600, font=("Fira Code", 14))
chat_log.pack(pady=10, padx=10)

# 🚀 Start everything
update_clock()
speak_greeting()
threading.Thread(target=continuous_listener, daemon=True).start()

app.mainloop()
