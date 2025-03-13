import object_detection
import keyboardInput
import time
import threading
import argparse


keyboardInputThread = threading.Thread(target=keyboardInput.startKeyboard, args=('any1', 'any2'))
keyboardInputThread.start()

objectDetectionThread = threading.Thread(target=object_detection.detection, args=('any1', 'any2'))
objectDetectionThread.start()