import cv2
import re

def detectar_camaras():
    cams_test = 20
    working_cameras = []
    for i in range(0, cams_test):
        cap = cv2.VideoCapture(i)
        test, frame = cap.read()
        if test:
            print("i : "+str(i)+" /// result: "+str(test))
            working_cameras.append(i)
        cap.release()

    # Update configuration.py with the first working camera
    if working_cameras:
        with open('configuration.py', 'r') as file:
            content = file.read()
        
        # Replace CAMERA_INDEX line with any value
        updated_content = re.sub(r'CAMERA_INDEX\s*=\s*.*', f'CAMERA_INDEX = {working_cameras[0]}', content)
        
        with open('configuration.py', 'w') as file:
            file.write(updated_content)
        
        print(f"Updated CAMERA_INDEX to {working_cameras[0]}")
    else:
        print("No working cameras found")

detectar_camaras()