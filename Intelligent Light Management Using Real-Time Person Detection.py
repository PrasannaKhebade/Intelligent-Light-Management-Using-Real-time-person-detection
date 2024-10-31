import cv2 
import numpy as np
import os
import time
import serial  # Library for Arduino communication

# Constants for detection thresholds and light control
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence required for detection
PERSON_CLASS_ID = 0          # Class ID corresponding to 'person' in YOLO model
LIGHT_OFF_DURATION = 5       # Duration (in seconds) to keep lights off after no person is detected

# Define paths for YOLO model configuration and weights
cfg_path = r"C:\Users\Dell\Downloads\yolov3.cfg"
weights_path = r"C:\Users\Dell\Downloads\yolov3.weights"
names_path = r"C:\Users\Dell\Downloads\coco.names"

# Ensure the necessary files for YOLO model exist
for path in [cfg_path, weights_path, names_path]:
    if not os.path.exists(path):
        print(f"File does not exist at {path}")
        exit()

# Load YOLO model from configuration and weights
net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)

# Load class names for YOLO detection
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize face detection model using Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

# Establish serial communication with Arduino (ensure the correct COM port is used)
arduino = serial.Serial('COM6', 9600)  # Replace 'COM6' with your system's correct port
time.sleep(2)  # Allow time for the connection to stabilize

# Initialize variables to manage detection states
last_detection_time = time.time()
light_on = True

while True:
    # Capture video frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture video")
        break

    # Preprocess the frame for YOLO detection
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)

    # Perform forward pass through the YOLO network
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    # Check for person detection based on model outputs
    person_detected = any(
        detection[5 + np.argmax(detection[5:])] > CONFIDENCE_THRESHOLD and
        np.argmax(detection[5:]) == PERSON_CLASS_ID
        for output in outputs for detection in output
    )

    # Update light status based on detection results
    current_time = time.time()
    if person_detected:
        if not light_on:
            print("Lights On")
            light_on = True
            arduino.write(b'ON\n')  # Command Arduino to turn the lights on
            
        cv2.putText(frame, "Lights On", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        last_detection_time = current_time  # Reset timer on successful detection
    else:
        if light_on and (current_time - last_detection_time) >= LIGHT_OFF_DURATION:
            print("Lights Off")
            light_on = False
            arduino.write(b'OFF\n')  # Command Arduino to turn the lights off
        
        if not person_detected and (current_time - last_detection_time) >= LIGHT_OFF_DURATION:
            cv2.putText(frame, "Lights Off", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Convert the captured frame to grayscale for face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces within the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue rectangle for face detection

    # Display the processed frame with annotations
    cv2.imshow('Webcam', frame)

    # Exit the loop if the 'Esc' key is pressed
    if cv2.waitKey(1) == 27:  # ASCII value of Esc is 27
        break

# Clean up resources: release video capture and close windows
cap.release()
cv2.destroyAllWindows()
arduino.close()  # Close serial communication with Arduino
