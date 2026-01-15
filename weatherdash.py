""" IF USING MAC USE THE COMMENTED OUT CODE AT THE BOTTOM"""

"""
🌦️ WeatherDash+ — Visual & Animated
Author: Param Sangani

✨ Upgrades:
- Sky-blue gradient with deeper tones
- Bold navy text for readability
- Center weather emoji overlay (☀️🌧️☁️)
- Auto-clear search bar
- Auto-refresh every 10 minutes
"""

import os
import math
import random
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherDashPlusAnimated:
    def __init__(self, root):
        self.root = root
        self.root.title("WeatherDash+ — by Param")
        self.root.geometry("520x480")
        self.root.minsize(320, 250)

        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.sky_gradient()

        self.city_var = tk.StringVar()
        self.last_city = None
        self.condition = "default"

        self.create_ui()
        self.root.bind("<Configure>", self.on_resize)

        # animation
        self.angle = 0
        self.rain_drops = []
        self.clouds = []
        self.animate()

    # 🌈 Draw background
    def sky_gradient(self):
        self.canvas.delete("sky")
        w = self.canvas.winfo_width() or 520
        h = self.canvas.winfo_height() or 480
        for i in range(h):
            r = int(80 + (173 - 80) * (i / h))
            g = int(170 + (216 - 170) * (i / h))
            b = int(230 + (255 - 230) * (i / h))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, w, i, fill=color, tags="sky")

    # 🌤️ Create UI
    def create_ui(self):
        self.entry = tk.Entry(self.root, textvariable=self.city_var, font=("Segoe UI", 14), width=25, justify="center")
        self.button = tk.Button(
            self.root,
            text="🔍 Get Weather",
            command=self.get_weather,
            bg="#1db954",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )

        # updated label colors for readability
        self.city_label = tk.Label(self.root, text="", fg="#003366", bg="#89CFF0", font=("Segoe UI", 22, "bold"))
        self.temp_label = tk.Label(self.root, text="", fg="#004c99", bg="#89CFF0", font=("Segoe UI", 38, "bold"))
        self.desc_label = tk.Label(self.root, text="", fg="#004c99", bg="#89CFF0", font=("Segoe UI", 15))
        self.extra_label = tk.Label(self.root, text="", fg="#005b80", bg="#89CFF0", font=("Segoe UI", 13))
        self.symbol_label = tk.Label(self.root, text="", bg="#89CFF0", font=("Segoe UI Emoji", 50))

        self.canvas.create_window(260, 40, window=self.entry)
        self.canvas.create_window(260, 80, window=self.button)
        self.canvas.create_window(260, 130, window=self.city_label)
        self.canvas.create_window(260, 230, window=self.symbol_label)
        self.canvas.create_window(260, 350, window=self.temp_label)
        self.canvas.create_window(260, 390, window=self.desc_label)
        self.canvas.create_window(260, 420, window=self.extra_label)

    # 🎞️ Main animation loop
    def animate(self):
        self.canvas.delete("symbol", "rain", "cloud")
        self.sky_gradient()

        if "clear" in self.condition:
            self.draw_sun()
        elif "rain" in self.condition or "drizzle" in self.condition:
            self.draw_rain()
        elif "cloud" in self.condition or "overcast" in self.condition:
            self.draw_clouds()

        self.root.after(50, self.animate)

    # ☀️ Sun animation
    def draw_sun(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x, y = w // 2, 230
        radius = 45
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#FFD93B", outline="", tags="symbol")
        for i in range(8):
            angle = math.radians(i * 45 + self.angle)
            dx, dy = 70 * math.cos(angle), 70 * math.sin(angle)
            self.canvas.create_line(x, y, x + dx, y + dy, fill="#FFD93B", width=4, tags="symbol")
        self.angle += 5

    # 🌧️ Rain animation
    def draw_rain(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if not self.rain_drops or random.random() < 0.3:
            self.rain_drops.append([random.randint(0, w), 0])
        new_drops = []
        for x, y in self.rain_drops:
            self.canvas.create_line(x, y, x + 2, y + 12, fill="#1e90ff", width=2, tags="rain")
            y += 12
            if y < h:
                new_drops.append([x, y])
        self.rain_drops = new_drops

    # ☁️ Cloud animation
    def draw_clouds(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if not self.clouds:
            for _ in range(3):
                self.clouds.append([random.randint(0, w), random.randint(150, 250), random.randint(80, 150)])
        for cloud in self.clouds:
            x, y, size = cloud
            self.canvas.create_oval(x - size, y - 30, x + size, y + 30, fill="#f0f0f0", outline="", tags="cloud")
            cloud[0] += 1
            if cloud[0] - size > w:
                cloud[0] = -size

    # 🌆 Fetch Weather
    def get_weather(self, auto=False):
        city = self.last_city if auto else self.city_var.get().strip()
        if not city:
            return
        params = {"q": city, "appid": API_KEY, "units": "metric"}

        try:
            r = requests.get(BASE_URL, params=params)
            data = r.json()
            if data.get("cod") != 200:
                self.city_label.config(text="❌ City not found")
                self.clear_labels()
                self.condition = "default"
                self.symbol_label.config(text="")
                return

            self.last_city = city
            city_name = f"{data['name']}, {data['sys']['country']}"
            temp = f"{data['main']['temp']}°C"
            desc = data["weather"][0]["description"].capitalize()
            humidity = f"💧 {data['main']['humidity']}%"

            # pick emoji
            lower = desc.lower()
            emoji = "☀️" if "clear" in lower else "🌧️" if "rain" in lower else "☁️" if "cloud" in lower else "🌈"

            self.city_label.config(text=city_name)
            self.temp_label.config(text=temp)
            self.desc_label.config(text=desc)
            self.extra_label.config(text=humidity)
            self.symbol_label.config(text=emoji)
            self.city_var.set("")  # clear entry
            self.condition = lower

            # Auto-refresh
            if not auto:
                self.root.after(600000, lambda: self.get_weather(auto=True))

        except Exception as e:
            self.city_label.config(text=f"⚠️ Error: {e}")
            self.clear_labels()
            self.symbol_label.config(text="")

    def clear_labels(self):
        for label in [self.temp_label, self.desc_label, self.extra_label]:
            label.config(text="")

    def on_resize(self, event):
        self.sky_gradient()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDashPlusAnimated(root)
    root.mainloop()

# 🌦️ WeatherWidget Pro — macOS Input Fix
# Author: Param Sangani
# """
# 
# import os
# import math
# import random
# import tkinter as tk
# import requests
# from dotenv import load_dotenv
# 
# # Load API key
# load_dotenv()
# API_KEY = os.getenv("API_KEY")
# BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
# 
# # --- Aesthetics Config ---
# FONT_MAIN = "Helvetica Neue"
# COLOR_TOP = "#4b6cb7"
# COLOR_BOT = "#182848"
# 
# 
# class WeatherWidget:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("WeatherWidget")
# 
#         # 1. SETUP FRAMELESS STATE INITIALLY
#         self.is_frameless = True
#         self.root.overrideredirect(True)
#         self.root.geometry("350x500")
# 
#         # 2. CENTER ON SCREEN
#         screen_width = self.root.winfo_screenwidth()
#         screen_height = self.root.winfo_screenheight()
#         x_c = int((screen_width / 2) - (350 / 2))
#         y_c = int((screen_height / 2) - (500 / 2))
#         self.root.geometry(f"+{x_c}+{y_c}")
# 
#         # 3. DRAG LOGIC (Works when frameless)
#         self.canvas = tk.Canvas(root, width=350, height=500, highlightthickness=0)
#         self.canvas.pack(fill="both", expand=True)
#         self.canvas.bind("<Button-1>", self.start_move)
#         self.canvas.bind("<B1-Motion>", self.do_move)
# 
#         # Animation State
#         self.condition = "clear"
#         self.angle = 0
#         self.rain_drops = []
#         self.clouds = []
# 
#         # --- UI ELEMENTS ---
#         self.draw_gradient()
# 
#         # Close Button
#         self.close_btn = tk.Button(root, text="×", font=(FONT_MAIN, 22), fg="white", bg=COLOR_TOP,
#                                    command=root.destroy, bd=0, highlightthickness=0)
#         self.canvas.create_window(325, 25, window=self.close_btn)
# 
#         # --- THE INPUT FIX ---
#         # We use a button that LOOKS like text to trigger the input mode
#         self.city_var = tk.StringVar()
#         self.entry = tk.Entry(root, textvariable=self.city_var, font=(FONT_MAIN, 14),
#                               bg=COLOR_TOP, fg="white", justify="center", bd=0, insertbackground="white")
# 
#         # When you click the entry, we MUST enable window borders to allow typing on Mac
#         self.entry.bind("<Button-1>", self.enable_input_mode)
#         self.entry.bind("<Return>", self.get_weather)
# 
#         # Place Entry
#         self.entry_window = self.canvas.create_window(175, 420, window=self.entry, width=200)
# 
#         # Underline
#         self.line = tk.Frame(root, height=2, bg="white")
#         self.canvas.create_window(175, 435, window=self.line, width=200)
# 
#         # Text Labels
#         self.temp_text = self.canvas.create_text(175, 250, text="--°", font=(FONT_MAIN, 90, "bold"), fill="white")
#         self.city_text = self.canvas.create_text(175, 160, text="WeatherDash", font=(FONT_MAIN, 22), fill="white")
#         self.desc_text = self.canvas.create_text(175, 330, text="Click here to search", font=(FONT_MAIN, 14, "italic"),
#                                                  fill="#ddd")
#         self.extra_text = self.canvas.create_text(175, 360, text="", font=(FONT_MAIN, 12), fill="#ccc")
# 
#         # Initial Animation
#         self.animate()
# 
#     # --- MAC INPUT FIX: TOGGLE FRAME ---
#     def enable_input_mode(self, event):
#         if self.is_frameless:
#             self.is_frameless = False
#             self.root.overrideredirect(False)  # Bring back borders
#             self.root.focus_force()  # Force focus
#             self.entry.focus_set()  # Focus the box
# 
#             # Helper: Hide the "Search" text hint
#             self.canvas.itemconfig(self.desc_text, text="Type & Enter...")
# 
#     def disable_input_mode(self):
#         if not self.is_frameless:
#             self.is_frameless = True
#             self.root.overrideredirect(True)  # Remove borders again
# 
#     # --- DRAGGING ---
#     def start_move(self, event):
#         self.x = event.x
#         self.y = event.y
# 
#     def do_move(self, event):
#         if self.is_frameless:  # Only drag when in widget mode
#             deltax = event.x - self.x
#             deltay = event.y - self.y
#             x = self.root.winfo_x() + deltax
#             y = self.root.winfo_y() + deltay
#             self.root.geometry(f"+{x}+{y}")
# 
#     # --- WEATHER & VISUALS ---
#     def draw_gradient(self):
#         self.canvas.delete("grad")
#         # Palette Selection
#         if "rain" in self.condition:
#             c1, c2 = "#203a43", "#2c5364"
#         elif "clear" in self.condition:
#             c1, c2 = "#2980b9", "#6dd5fa"
#         elif "cloud" in self.condition:
#             c1, c2 = "#606c88", "#3f4c6b"
#         else:
#             c1, c2 = "#4b6cb7", "#182848"
# 
#         h = 500
#         r1, g1, b1 = self.root.winfo_rgb(c1)
#         r2, g2, b2 = self.root.winfo_rgb(c2)
#         r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
#         r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256
# 
#         for i in range(h):
#             r = int(r1 + (r2 - r1) * (i / h))
#             g = int(g1 + (g2 - g1) * (i / h))
#             b = int(b1 + (b2 - b1) * (i / h))
#             self.canvas.create_line(0, i, 350, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="grad")
#         self.canvas.tag_lower("grad")
# 
#     def animate(self):
#         self.canvas.delete("anim")
#         if "clear" in self.condition:
#             self.anim_sun()
#         elif "rain" in self.condition:
#             self.anim_rain()
#         elif "cloud" in self.condition:
#             self.anim_clouds()
#         self.root.after(50, self.animate)
# 
#     def anim_sun(self):
#         cx, cy = 175, 100
#         for i in range(12):
#             angle = math.radians(self.angle + i * 30)
#             self.canvas.create_line(cx + 40 * math.cos(angle), cy + 40 * math.sin(angle),
#                                     cx + 55 * math.cos(angle), cy + 55 * math.sin(angle),
#                                     fill="#FFD700", width=3, tags="anim")
#         self.canvas.create_oval(cx - 30, cy - 30, cx + 30, cy + 30, fill="#FFA500", outline="#FFD700", tags="anim")
#         self.angle += 2
# 
#     def anim_rain(self):
#         if random.random() < 0.6: self.rain_drops.append([random.randint(0, 350), 0])
#         self.rain_drops = [[x, y + 15] for x, y in self.rain_drops if y < 500]
#         for x, y in self.rain_drops:
#             self.canvas.create_line(x, y, x, y + 15, fill="#a8d8ea", width=1, tags="anim")
# 
#     def anim_clouds(self):
#         if len(self.clouds) < 4 and random.random() < 0.02: self.clouds.append([-50, random.randint(20, 150)])
#         self.clouds = [[x + 0.5, y] for x, y in self.clouds if x < 400]
#         for x, y in self.clouds:
#             for dx, dy in [(0, 0), (20, -10), (40, 0)]:
#                 self.canvas.create_oval(x + dx, y + dy, x + dx + 40, y + dy + 30, fill="#e0e0e0", outline="",
#                                         tags="anim")
# 
#     def get_weather(self, event=None):
#         city = self.city_var.get()
#         if not city: return
# 
#         # DISABLE INPUT MODE IMMEDIATELY (Return to aesthetic state)
#         self.disable_input_mode()
# 
#         try:
#             r = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
#             data = r.json()
# 
#             if data.get("cod") != 200:
#                 self.canvas.itemconfig(self.city_text, text="Not Found")
#                 return
# 
#             self.condition = data['weather'][0]['description'].lower()
#             self.canvas.itemconfig(self.temp_text, text=f"{int(data['main']['temp'])}°")
#             self.canvas.itemconfig(self.city_text, text=data['name'].upper())
#             self.canvas.itemconfig(self.desc_text, text=data['weather'][0]['description'].capitalize())
#             self.canvas.itemconfig(self.extra_text, text=f"Humidity: {data['main']['humidity']}%")
# 
#             self.draw_gradient()
#             self.city_var.set("")  # clear box
# 
#         except Exception as e:
#             print(e)
# 
# 
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = WeatherWidget(root)
#     root.mainloop()
