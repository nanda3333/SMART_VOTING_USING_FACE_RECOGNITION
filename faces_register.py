import cv2
import pickle
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox

# Create data folder if not exists
if not os.path.exists('data/'):
    os.makedirs('data/')

# GUI for Aadhar input
def start_registration():
    name = aadhar_entry.get()
    if not name.strip():
        messagebox.showerror("Input Error", "Please enter a valid Aadhar number.")
        return

    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces_data = []
    i = 0
    framesTotal = 51
    captureAfterFrame = 2

    while True:
        ret, frame = video.read()
        if not ret or frame is None:
            print("Failed to grab frame from camera.")
            messagebox.showerror("Camera Error", "Failed to access the camera. Please make sure it's connected and not in use by another app.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w]
            resized_img = cv2.resize(crop_img, (50, 50))
            if len(faces_data) <= framesTotal and i % captureAfterFrame == 0:
                faces_data.append(resized_img)
            i += 1
            cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

        cv2.imshow('Face Registration', frame)
        k = cv2.waitKey(1)
        if k == ord('q') or len(faces_data) >= framesTotal:
            break

    video.release()
    cv2.destroyAllWindows()

    # Convert to array and reshape
    faces_data_np = np.asarray(faces_data).reshape((framesTotal, -1))

    # Store name
    if 'names.pkl' not in os.listdir('data/'):
        names = [name] * framesTotal
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)
    else:
        with open('data/names.pkl', 'rb') as f:
            names = pickle.load(f)
        names += [name] * framesTotal
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)

    # Store faces
    if 'faces_data.pkl' not in os.listdir('data/'):
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces_data_np, f)
    else:
        with open('data/faces_data.pkl', 'rb') as f:
            faces = pickle.load(f)
        faces = np.append(faces, faces_data_np, axis=0)
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces, f)

    messagebox.showinfo("Success", "Face registered successfully!")


# Tkinter Interface
root = tk.Tk()
root.title("Face Registration")
root.geometry("400x250")
root.configure(bg="#f0f8ff")

tk.Label(root, text="Face Registration", font=("Arial", 20, "bold"), bg="#f0f8ff", fg="#333").pack(pady=20)
tk.Label(root, text="Enter Aadhar Number:", font=("Arial", 14), bg="#f0f8ff").pack()

aadhar_entry = tk.Entry(root, font=("Arial", 14), width=30)
aadhar_entry.pack(pady=10)

tk.Button(root, text="Start Registration", font=("Arial", 12, "bold"), bg="#007bff", fg="white", command=start_registration).pack(pady=20)

root.mainloop()
