from time import sleep
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
from configuration import *

def show_frame():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        root.destroy()
        return
    
    # Convert to grayscale if the image has multiple channels
    if len(frame.shape) == 3:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    else:
        gray = frame
    
    # Find the hottest point (brightest pixel in grayscale)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(gray)
    
    # Calculate percentage based on the brightest pixel
    temp_min = -40
    temp_max = 80
    temp = temp_min + (max_val / 255.0) * (temp_max - temp_min)
    if temp == 80:
        print('FIRE WARNING!')
        sleep(5)  
    # Draw a circle at the hottest point on the original frame
    cv.circle(frame, max_loc, 10, (0, 255, 0), 2)
    
    # Add temperature text
    if SHOW_TEMPERATURE_TEXT:
        temp_text = f"Max Temp: {temp:.1f}C"
        cv.putText(frame, temp_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
    # Resize frame to fit the window
    if RESIZE_WINDOW:
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        if window_width > 1 and window_height > 1:
            frame = cv.resize(frame, (window_width, window_height))

    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)


#Load webcam
cap = cv.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Root window
root = tk.Tk()
root.attributes('-fullscreen', True)  # Make window fullscreen
lmain = tk.Label(root)
lmain.pack(fill=tk.BOTH, expand=True)
root.update()  # Ensure window dimensions are available
show_frame()
root.mainloop()

cap.release()