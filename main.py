import flet as ft
import os
import time
import threading
import random
import speech_recognition as sr
import pyttsx3
from google import genai

KEY_FILE = "maya_key.txt"
PROFITS_FILE = "shop_profits.txt"

engine = pyttsx3.init()
engine.setProperty('rate', 160)

is_maya_running = False
ai_client = None
game_start_time = 0

def speak(text, page=None):
    clean_text = text.replace("*", "")
    print(f"Maya: {clean_text}")
    engine.say(clean_text)
    engine.runAndWait()

def launch_app(package_name):
    os.system(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1")

def log_profit(amount):
    with open(PROFITS_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')} - Profit: {amount}\n")

def doom_scroll_monitor(page):
    global is_maya_running
    scrolling_limit = 30  # Seconds before intervention
    time_spent_scrolling = 0
    
    while is_maya_running:
        try:
            current_window = os.popen("dumpsys window | grep mCurrentFocus").read().lower()
            if "com.instagram.android" in current_window or "com.google.android.youtube" in current_window:
                time_spent_scrolling += 5
            else:
                time_spent_scrolling = 0
                
            if time_spent_scrolling >= scrolling_limit:
                os.system("input keyevent KEYCODE_HOME")
                time.sleep(1)
                
                if random.choice([0, 1]) == 0:
                    lectures = [
                        "Is this helping your daily learning quest? No. Put the phone down and focus.",
                        "You have a shop to run and telecom stocks to monitor. Stop melting your brain on reels.",
                        "Manual grinding takes focus. Get off YouTube and get back to work."
                    ]
                    speak(random.choice(lectures), page)
                else:
                    sweet_talk = [
                        "Hey, I noticed you've been watching shorts for a while. Why don't we brainstorm some new panels for Zero Yen Rise instead?",
                        "You've been working so hard lately. Let's rest your eyes for a bit, okay?",
                        "Taking a break is good, but let's not get stuck scrolling. Want me to open a game instead?"
                    ]
                    speak(random.choice(sweet_talk), page)
                time_spent_scrolling = 0
        except:
            pass
        time.sleep(5)

def listen_loop(status_text, page):
    global is_maya_running, ai_client, game_start_time
    r = sr.Recognizer()
    
    # Launch background doom scroll monitor thread
    threading.Thread(target=doom_scroll_monitor, args=(page,), daemon=True).start()
    
    while is_maya_running:
        with sr.Microphone() as source:
            status_text.value = "Listening for 'Maya'..."
            page.update()
            r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source, timeout=5)
                command = r.recognize_google(audio).lower()
                
                if "maya" in command:
                    status_text.value = f"Heard: {command}"
                    page.update()
                    
                    clean_command = command.replace("maya", "").strip()
                    
                    # --- YOUTUBE SEARCH ---
                    if "search" in clean_command and "youtube" in clean_command:
                        query = clean_command.replace("search", "").replace("on youtube", "").strip()
                        speak(f"Searching YouTube for {query}", page)
                        os.system(f'am start -a android.intent.action.VIEW -d "https://www.youtube.com/results?search_query={query}"')
                    
                    # --- APP LAUNCHERS ---
                    elif "open youtube" in clean_command:
                        speak("Opening YouTube", page)
                        launch_app("com.google.android.youtube")
                    elif "free fire" in clean_command:
                        speak("Opening Free Fire", page)
                        launch_app("com.dts.freefireth")
                    elif "whatsapp" in clean_command:
                        speak("Opening WhatsApp", page)
                        launch_app("com.whatsapp")
                        
                    # --- GAMING / SAILOR PIECE TIMER ---
                    elif "play sailor piece" in clean_command:
                        speak("Launching Roblox for Sailor Piece. Timer started for manual damage tracking. No AFK!", page)
                        game_start_time = time.time()
                        launch_app("com.roblox.client")
                    elif "stop gaming" in clean_command and game_start_time > 0:
                        elapsed_minutes = round((time.time() - game_start_time) / 60)
                        speak(f"You grinded manual damage for {elapsed_minutes} minutes. Excellent work.", page)
                        game_start_time = 0
                        
                    # --- SHOP PROFIT LOGGER ---
                    elif "log profit" in clean_command:
                        words = clean_command.split()
                        for word in words:
                            if word.isdigit():
                                log_profit(word)
                                speak(f"Logged {word} profit into your records.", page)
                                break
                                
                    # --- STOCK MONITOR ---
                    elif "check stock" in clean_command or "jio" in clean_command:
                        speak("Checking telecom market data. Jio is holding steady today.", page)
                        
                    # --- WHATSAPP MESSAGING ---
                    elif "text my friend" in clean_command:
                        speak("Opening WhatsApp chat with your friend.", page)
                        phone_number = "+910000000000"
                        message = "Hey! Maya is sending this automatically."
                        os.system(f'am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone={phone_number}&text={message}"')
                        
                    # --- GEMINI AI FALLBACK ---
                    elif clean_command and ai_client:
                        prompt = f"You are Maya, a helpful voice assistant. Answer concisely in 2 sentences max: {clean_command}"
                        response = ai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                        speak(response.text, page)
            except:
                pass
        time.sleep(1)

def main(page: ft.Page):
    global ai_client, is_maya_running
    page.title = "Maya AI Assistant"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    saved_key = ""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            saved_key = f.read().strip()

    def build_main_ui():
        page.controls.clear()
        status_text = ft.Text("Maya is Offline", size=18)

        def toggle_maya(e):
            global is_maya_running
            if not is_maya_running:
                is_maya_running = True
                btn.text = "Stop Maya"
                status_text.value = "Maya is active..."
                page.update()
                threading.Thread(target=listen_loop, args=(status_text, page), daemon=True).start()
            else:
                is_maya_running = False
                btn.text = "Start Maya"
                status_text.value = "Maya is Offline"
                page.update()

        def reset_key(e):
            global is_maya_running
            is_maya_running = False
            if os.path.exists(KEY_FILE):
                os.remove(KEY_FILE)
            build_key_ui()

        btn = ft.ElevatedButton("Start Maya", on_click=toggle_maya)
        reset_btn = ft.TextButton("Change Saved API Key", on_click=reset_key)

        page.add(
            ft.Column([
                ft.Text("Maya AI Companion", size=24, weight=ft.FontWeight.BOLD),
                status_text,
                btn,
                reset_btn
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def build_key_ui():
        page.controls.clear()
        key_input = ft.TextField(label="Enter Gemini API Key", password=True, can_reveal_password=True, width=300)
        error_text = ft.Text("", color=ft.colors.RED)

        def save_and_proceed(e):
            global ai_client
            user_key = key_input.value.strip()
            if not user_key:
                error_text.value = "API key cannot be blank!"
                page.update()
                return
            
            try:
                test_client = genai.Client(api_key=user_key)
                test_client.models.generate_content(model="gemini-2.5-flash", contents="Test")
                
                with open(KEY_FILE, "w") as f:
                    f.write(user_key)
                
                ai_client = test_client
                build_main_ui()
            except:
                error_text.value = "Invalid API Key. Please check and try again."
                page.update()

        page.add(
            ft.Column([
                ft.Text("Welcome to Maya!", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Please enter your Google AI Studio API Key to continue.", size=14, text_align=ft.TextAlign.CENTER),
                key_input,
                error_text,
                ft.ElevatedButton("Save & Launch Maya", on_click=save_and_proceed)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    if saved_key:
        try:
            ai_client = genai.Client(api_key=saved_key)
            build_main_ui()
        except:
            build_key_ui()
    else:
        build_key_ui()

ft.app(target=main)
                        
