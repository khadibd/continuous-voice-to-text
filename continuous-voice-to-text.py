# -*- coding: utf-8 -*-
"""
Created on Jan Dec 1 12:04:50 2019

@author: Bouadi Khadija
"""


import tkinter as tk
from tkinter import Scrollbar, Text
import speech_recognition as sr
from datetime import datetime
import threading

class ContinuousTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Live Transcription Vocale (Low Latency)")

        # Text area
        self.text_widget = Text(
            root,
            wrap='word',
            font=('Arial', 12),
            height=15,
            width=70
        )
        self.text_widget.pack(padx=10, pady=10)

        # Scrollbar
        scrollbar = Scrollbar(root, command=self.text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Buttons
        self.start_button = tk.Button(
            root,
            text="▶️ Start Listening",
            font=('Arial', 11),
            command=self.start_listening
        )
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(
            root,
            text="⏹️ Stop Listening",
            font=('Arial', 11),
            command=self.stop_listening,
            state='disabled'
        )
        self.stop_button.pack(pady=5)

        self.stop_flag = False

    def start_listening(self):
        self.stop_flag = False
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.text_widget.insert(tk.END, "[Listening started]\n")
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        self.stop_flag = True
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.text_widget.insert(tk.END, "[Listening stopped]\n")

    def listen_loop(self):
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.6  # Short silence = faster result

        try:
            with sr.Microphone() as source:
                self.text_widget.insert(tk.END, "[Calibrating microphone...]\n")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                self.text_widget.insert(tk.END, "[Speak now]\n")

                while not self.stop_flag:
                    try:
                        audio = recognizer.listen(
                            source,
                            timeout=None,
                            phrase_time_limit=4
                        )

                        try:
                            text = recognizer.recognize_google(
                                audio,
                                language="fr-FR"
                            )
                            self.text_widget.insert(tk.END, text + "\n")
                            self.text_widget.see(tk.END)
                            self.save_to_file(text)

                        except sr.UnknownValueError:
                            pass  # Ignore noise
                        except sr.RequestError as e:
                            self.text_widget.insert(
                                tk.END,
                                f"[Google API error: {e}]\n"
                            )

                    except Exception as e:
                        self.text_widget.insert(tk.END, f"[Error: {e}]\n")

        except Exception as e:
            self.text_widget.insert(
                tk.END,
                f"[Microphone error: {e}]\n"
            )

    def save_to_file(self, text):
        with open("transcription.txt", "a", encoding="utf-8") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {text}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContinuousTranscriptionApp(root)
    root.mainloop()
