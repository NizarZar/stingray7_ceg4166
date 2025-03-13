import os
import argparse
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
import threading

# Import Picamera2 libraries
from picamera2 import Picamera2
import cv2  # Still needed for image processing, not camera access

class Video_Picam2:
    def __init__(self, resolution=(640, 480), framerate=60):
        # Initialize Picamera2
        self.picam2 = Picamera2()
        
        # Configure the camera
        config = self.picam2.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"},
            controls={"FrameDurationLimits": (int(1/framerate * 1000000), 1000000)},
        )
        self.picam2.configure(config)
        
        # Start the camera
        self.picam2.start()
        
        # Get initial frame
        self.frame = self.picam2.capture_array()
        self.stopped = False
    
    def start(self):
        Thread(target=self.update, args=()).start()  # Start the thread to read frames
        return self
    
    def update(self):
        while True:
            if self.stopped:
                self.picam2.stop()  # Stop the camera when requested
                return
            self.frame = self.picam2.capture_array()  # Capture the next frame
    
    def read(self):
        return self.frame  # Return the most recent frame
    
    def stop(self):
        self.stopped = True  # Signal the thread to stop

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', required=True)
parser.add_argument('--graph', default='detect.tflite')
parser.add_argument('--labels', default='labelmap.txt')
parser.add_argument('--threshold', default=0.5)
parser.add_argument('--resolution', default='600x300')

args = parser.parse_args()

model = args.modeldir
graph_n = args.graph
label_ = args.labels
minimum_confidence = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)

# Import TensorFlow Lite interpreter
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

# Set up model paths
current_dir = os.getcwd()
tflite_directory = os.path.join(current_dir, model, graph_n)
label_destination = os.path.join(current_dir, model, label_)

# Load label map
with open(label_destination, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

if labels[0] == '???':
    del(labels[0])

# Load TensorFlow Lite model
model_interpreter = Interpreter(model_path=tflite_directory)
model_interpreter.allocate_tensors()

# Get model details
input_details = model_interpreter.get_input_details()
output_details = model_interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize Picamera2 for object detection
camera = Video_Picam2(resolution=(imW, imH), framerate=30).start()
time.sleep(1)  # Allow camera to warm up

def detection(any1, any2):
    frame_count = 0
    start_time = cv2.getTickCount()
    while True:
        # Get frame from camera
        original_frame = camera.read()
        if original_frame is None:
            print("Error: Could not capture frame.")
            continue  # Skip this frame

        # Copy the frame to avoid modification issues
        frame = original_frame.copy()
        
        # Picam2 returns RGB format already, so no need for BGR to RGB conversion
        # But we'll make sure we have the right format
        if frame.shape[2] == 3 and frame.dtype == np.uint8:
            frame_rgb = frame
        else:
            print("Warning: Unexpected frame format, converting to RGB")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
        # Resize to match model input
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)
        
        # Normalize pixel values if using a floating model
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std
            
        # Perform detection
        model_interpreter.set_tensor(input_details[0]['index'], input_data)
        model_interpreter.invoke()
        
        # Get detection results
        boxes = model_interpreter.get_tensor(output_details[0]['index'])[0]
        classes = model_interpreter.get_tensor(output_details[1]['index'])[0]
        scores = model_interpreter.get_tensor(output_details[2]['index'])[0]
        
        # Draw result boxes
        for i in range(len(scores)):
            if ((scores[i] > minimum_confidence) and (scores[i] <= 1.0)):
                # Get box coordinates
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))
                
                # Draw rectangle
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                
                # Add label
                object_name = labels[int(classes[i])]
                label = '%s: %d%%' % (object_name, int(scores[i]*100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, labelSize[1] + 10)
                cv2.rectangle(frame, 
                              (xmin, label_ymin-labelSize[1]-10), 
                              (xmin+labelSize[0], label_ymin+baseLine-10), 
                              (255, 255, 255), 
                              cv2.FILLED)
                cv2.putText(frame, 
                            label, 
                            (xmin, label_ymin-7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.7, 
                            (0, 0, 0), 
                            2)
        
        # frame rate top of screen:
        frame_count+=1
        if frame_count % 30 == 0:
            end_time = cv2.getTickCount()
            time_taken = (end_time - start_time) / cv2.getTickFrequency()
            fps = frame_count / time_taken
            start_time = end_time

            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Display the frame
        cv2.imshow('Object Detection with Picam2', frame)
        
        # Check for exit request
        if cv2.waitKey(1) == ord('q'):
            print("\nExiting the application")
            break
    
    # Clean up
    cv2.destroyAllWindows()
    camera.stop()
