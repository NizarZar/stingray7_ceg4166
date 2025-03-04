import time
import rotationSpeed_Graph  # Import the module

KP = 15   # Proportional gain
KD = 0    # Derivative gain
KI = 3.75 # Integral gain

sampleTime = 0.4  # Keep this value as 0.4 seconds

# Access the encoders from rotationSpeed_Graph
leftWheelEncoder = rotationSpeed_Graph.leftEncoderCount
rightWheelEncoder = rotationSpeed_Graph.rightEncoderCount

def straight(timer):
    move_pid(leftWheelEncoder, rightWheelEncoder, timer, direction="forward")

def backward(timer):
    move_pid(leftWheelEncoder, rightWheelEncoder, timer, direction="backward")

def left(timer):
    move_pid(leftWheelEncoder, rightWheelEncoder, timer, direction="left")

def right(timer):
    move_pid(leftWheelEncoder, rightWheelEncoder, timer, direction="right")

def move_pid(leftWheelEncoder, rightWheelEncoder, timer, direction):
    leftWheelEncoder.resetTicks()
    rightWheelEncoder.resetTicks()
    
    targetIteration = 10
    baseSpeedLeft = 1530
    baseSpeedRight = 1470
    maxSpeedLeft = baseSpeedLeft
    maxSpeedRight = baseSpeedRight

    leftPError = 0
    rightPError = 0
    leftSError = 0
    rightSError = 0
    target = 0  # Initialize target ticks

    timeout = time.time() + timer
    i = 0  # Iteration counter

    while time.time() < timeout:
        leftError = target - leftWheelEncoder.getTicks()
        rightError = target - rightWheelEncoder.getTicks()

        # PID control calculations
        if abs(leftError) > 1 or i == 0:
            leftSpeed = baseSpeedLeft + (leftError * KP) + ((leftError - leftPError) * KD) + (leftSError * KI)
            leftSpeed = max(min(maxSpeedLeft, leftSpeed), 1720)

        if abs(rightError) > 1 or i == 0:
            rightSpeed = baseSpeedRight - (rightError * KP) - ((rightError - rightPError) * KD) - (rightSError * KI)
            rightSpeed = min(max(maxSpeedRight, rightSpeed), 1280)

        # Set motor speeds based on direction
        if direction == "forward":
            rotationSpeed_Graph.Robot_forward(leftSpeed, rightSpeed)
        elif direction == "backward":
            rotationSpeed_Graph.Robot_forward(leftSpeed,rightSpeed)
            rotationSpeed_Graph.Robot_reverse()
        elif direction == "left":
            rotationSpeed_Graph.Robot_left()
        elif direction == "right":
            rotationSpeed_Graph.Robot_right()

        time.sleep(sampleTime)

        leftPError = leftError
        rightPError = rightError
        leftSError += leftError
        rightSError += rightError

        target += targetIteration  # Update target
        i += 1  # Increment iteration count

    rotationSpeed_Graph.motorStop()
    time.sleep(0.1)
    rotationSpeed_Graph.motorStop()
