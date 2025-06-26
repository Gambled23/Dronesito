import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk

def show_frame():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        root.destroy()
        return
    # Resize frame to fit the window
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    if window_width > 1 and window_height > 1:
        frame = cv.resize(frame, (window_width, window_height))
    heatmap = cv.applyColorMap(frame, cv.COLORMAP_JET)
    img = Image.fromarray(heatmap)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

cap = cv.VideoCapture(2)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

root = tk.Tk()
root.attributes('-fullscreen', True)  # Make window fullscreen
lmain = tk.Label(root)
lmain.pack(fill=tk.BOTH, expand=True)
root.update()  # Ensure window dimensions are available
show_frame()
root.mainloop()

cap.release()