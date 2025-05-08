import cv2
import tkinter as tk
from PIL import Image, ImageTk
import csv
import time
from datetime import datetime
import pyttsx3
import os
import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# --- Load Face Recognition Model ---
with open('data/names.pkl', 'rb') as f:
    LABELS = pickle.load(f)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- TTS ---
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

# --- Vote Recording ---
def record_vote(name, party):
    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
    filename = "Votes.csv"
    exist = os.path.isfile(filename)

    if check_if_exists(name):
        speak("YOU HAVE ALREADY VOTED")
        return

    with open(filename, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not exist:
            writer.writerow(['NAME', 'VOTE', 'DATE', 'TIME'])
        writer.writerow([name, party, date, timestamp])

    speak("YOUR VOTE HAS BEEN RECORDED")
    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")

# --- Check if user has already voted ---
def check_if_exists(value):
    try:
        with open("Votes.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == value:
                    return True
    except FileNotFoundError:
        pass
    return False

# --- GUI Setup ---
window = tk.Tk()
window.title("Voting System")
window.geometry("1280x720")

# Background

bg_image = Image.open("vote1.jpeg").resize((1280, 720))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(window, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Camera feed canvas
canvas = tk.Canvas(window, width=320, height=240, bg="black", highlightthickness=2)
canvas.place(x=900, y=220)  # Bottom right

cap = cv2.VideoCapture(0)

recognized_person = tk.StringVar()
recognized_person.set("Detecting...")

def update_frame():
    global last_recognized_person
    ret, frame = cap.read()
    if ret:
        frame_resized = cv2.resize(frame, (320, 240))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_img = frame_resized[y:y+h, x:x+w]
                resized_face = cv2.resize(face_img, (50, 50)).flatten().reshape(1, -1)
                name = knn.predict(resized_face)[0]
                recognized_person.set(f"{name}")
                last_recognized_person = name  # <- store for later use

                cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame_resized, str(name), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            recognized_person.set("Detecting...")

        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.imgtk = imgtk

    window.after(10, update_frame)

update_frame()

# Label for recognized person
tk.Label(window, textvariable=recognized_person, font=('Arial', 20, 'bold'), bg="white", fg="green").place(x=100, y=440)

# --- Buttons ---
def vote(party):
    name = recognized_person.get()
    if name == "Detecting...":
        speak("FACE NOT DETECTED")
    else:
        record_vote(name, party)

btn_style = {'width': 20, 'height': 2, 'font': ('Arial', 12, 'bold'), 'bg': '#007bff', 'fg': 'white'}

tk.Button(window, text="Vote BJP", command=lambda: vote("BJP"), **btn_style).place(x=100, y=300)
tk.Button(window, text="Vote Congress", command=lambda: vote("CONGRESS"), **btn_style).place(x=100, y=360)
tk.Button(window, text="Vote AAP", command=lambda: vote("AAP"), **btn_style).place(x=100, y=420)
tk.Button(window, text="Vote NOTA", command=lambda: vote("NOTA"), **btn_style).place(x=100, y=480)

window.mainloop()
cap.release()
