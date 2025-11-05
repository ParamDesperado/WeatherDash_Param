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
