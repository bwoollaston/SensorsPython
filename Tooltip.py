import tkinter as tk
from tkinter import ttk
import time

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.background = "#F5F0EE"
        self.foreground = "#0F0E0E"
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        time.sleep(1)
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx()
        y += self.widget.winfo_rooty() + self.widget.winfo_height()

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        self.label = ttk.Label(self.tooltip, text=self.text, background=self.Background, foreground=self.foreground, relief="solid", borderwidth=1, padding=2)
        self.label.pack()
    @property
    def Background(self):
        return self.background
    @Background.setter
    def Background(self,value):
        self.background = value
    @property
    def Foreground(self):
        return self.foreground
    @Foreground.setter
    def Foreground(self,value):
        self.foreground = value

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None