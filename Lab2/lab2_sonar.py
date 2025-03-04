import pigpio
import termios
import tty
import sys
import pid_controller
import rotationSpeed_Graph  # Import motor control functions

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

raspi = pigpio.pi()

while True:
    char = getch()
    
    if char == "w":
        print("Moving forward")
        pid_controller.straight(1)  # Move forward for 1 second

    elif char == "s":
        print("Moving backward")
        pid_controller.backward(1)  # Move backward for 1 second

    elif char == "a":
        print("Turning left")
        pid_controller.left(0.25)  # Turn left for 1 second

    elif char == "d":
        print("Turning right")
        pid_controller.right(0.25)  # Turn right for 1 second

    elif char == "f":
        print("Stopping program.")
        rotationSpeed_Graph.motorStop()  # Stop motors before exiting
        raspi.stop()
        exit()

    # Stop motors when no key is pressed
    rotationSpeed_Graph.motorStop()
