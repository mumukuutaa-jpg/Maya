import flet as ft
import os
import time
import threading
import speech_recognition as sr
import pyttsx3
from google import genai

# Initialize engines
engine = pyttsx3.init()
engine.setProperty('rate', 160)
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
ai_client = genai.Client(api_key=GEMINI_API_KEY)

is_maya_running = False

def speak(text, page=None):
    clean_text = text.replace("*", "")
    print(f"Maya: {clean_text}")
    engine.say(clean_text)
    engine.runAndWait()

def listen_loop(status_text, page):
    global is_maya_running
    r = sr.Recognizer()
    
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
                    if "open youtube" in clean_command:
                        speak("Opening YouTube", page)
                        os.system("monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1")
                    elif clean_command:
                        # Gemini AI fallback for open-ended questions
                        prompt = f"You are Maya, a helpful voice assistant. Answer in 2 sentences max: {clean_command}"
                        response = ai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                        speak(response.text, page)
            except:
                pass
        time.sleep(1)

def main(page: ft.Page):
    page.title = "Maya AI Assistant"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
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

    btn = ft.ElevatedButton("Start Maya", on_click=toggle_maya)

    page.add(
        ft.Column([
            ft.Text("Maya AI Companion", size=24, weight=ft.FontWeight.BOLD),
            status_text,
            btn
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
  
