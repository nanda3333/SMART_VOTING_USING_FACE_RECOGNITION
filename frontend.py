import tkinter as tk
from tkinter import messagebox
import subprocess

# Create main window
window = tk.Tk()
window.title("Face Recognition Voting System")
window.geometry("800x500")
window.configure(bg="#8d3246")  

# --- Styles ---
HEADER_FONT = ("Helvetica", 24, "bold")
BUTTON_FONT = ("Arial", 12, "bold")
BTN_BG = "#007bff"
BTN_HOVER = "#0056b3"
BTN_FG = "white"
CARD_BG = "#ffd700"
TEXT_COLOR = "#333333"

# --- Hover effect for buttons ---
def on_enter(e):
    e.widget["background"] = BTN_HOVER

def on_leave(e):
    e.widget["background"] = BTN_BG

# --- Run external scripts ---
def run_registration():
    try:
        subprocess.Popen(["python3", "faces_register.py"])
    except FileNotFoundError:
        messagebox.showerror("Error", "faces_register.py not found!")

def run_voting():
    try:
        subprocess.Popen(["python3", "vote.py"])
    except FileNotFoundError:
        messagebox.showerror("Error", "vote.py not found!")

# --- Title ---
title_label = tk.Label(window, text="SMART VOTING USING FACE RECOGNITION", font=HEADER_FONT, bg="#ffc0cb", fg="#ff7f24")
title_label.pack(pady=40)

# --- Central card frame ---
frame = tk.Frame(window, bg=CARD_BG, bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=200)

# --- Buttons inside frame ---
register_btn = tk.Button(frame, text="Register New Voter", font=BUTTON_FONT, bg=BTN_BG, fg=BTN_FG,
                         activebackground=BTN_HOVER, activeforeground="white", bd=0,
                         command=run_registration)
register_btn.pack(pady=20, ipadx=10, ipady=5)
register_btn.bind("<Enter>", on_enter)
register_btn.bind("<Leave>", on_leave)

vote_btn = tk.Button(frame, text="Start Voting", font=BUTTON_FONT, bg=BTN_BG, fg=BTN_FG,
                     activebackground=BTN_HOVER, activeforeground="white", bd=0,
                     command=run_voting)
vote_btn.pack(pady=10, ipadx=10, ipady=5)
vote_btn.bind("<Enter>", on_enter)
vote_btn.bind("<Leave>", on_leave)

# Run the app
window.mainloop()
