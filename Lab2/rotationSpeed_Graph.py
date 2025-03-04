#Import Libraries
import threading
import time
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import pigpio
import RPi.GPIO as GPIO
from WheelEncoderGPIO import WheelEncoder
from PlotDataRobot import multiplePlots
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
        
servos = [23,24]
raspi= pigpio.pi()

samples = 5

#creation of two encoders using WheelEncoder class
leftEncoderCount = WheelEncoder(11, 32, 5.65/2)
rightEncoderCount = WheelEncoder(13, 33, 5.65/2)

xmax = 5
plotData = multiplePlots(leftEncoderCount, rightEncoderCount,
    samples, xmax)

#Returning values to plot the data
def loopData(self):
    plotData.updateData()
    return plotData.p011, plotData.p012, plotData.p021, plotData.p022
	
def Left_forward(n):
    raspi.set_servo_pulsewidth(servos[0], n)
    
def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], 1700)
	
def Left_stop():
    raspi.set_servo_pulsewidth(servos[0], 0)

#Value for servo speed forward now an argument that must be passed    
def Right_forward(n):
    raspi.set_servo_pulsewidth(servos[1], n)
    
def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], 1300)
    
def Right_stop():
    raspi.set_servo_pulsewidth(servos[1], 0)

#robot forward function takes two arguments for each motors servo speed
def Robot_forward(n, m):
    Left_forward(n)
    Right_forward(m)
    time.sleep(.1)
    
def Robot_reverse():
    Left_reverse()
    Right_reverse()
    time.sleep(.1)
    
def Robot_stop():
    Left_stop()
    Right_stop()
    time.sleep(.1)
        
def Robot_right():
    Left_forward(1300)
    Right_reverse()

def Robot_left():
    Right_forward(1700)
    Left_reverse()

#Function to stop all motors    
def motorStop():
    for s in servos:
        raspi.set_servo_pulsewidth(s,0)
     
#Function for encoder output takes wheelEncoder object and a name for the encoder as #arguments
def Encoders(wheelEncoder, name):
    while(True):
        dist = wheelEncoder.getCurrentDistance()
        totDist = wheelEncoder.getTotalDistance()
        # print("\n{} Distance: {}cm".format(name, dist))
        # print("\n{} Ticks: {}".format(name, wheelEncoder.getTicks()))
        # print("\n{} Total Distance: {}cm".format(name, totDist))
        # print("\n{} Total Ticks: {}".format(name, wheelEncoder.getTotalTicks()))
        time.sleep(0.01)


#create a function to move the robot, with 2 arguments
#remember to add the functions that you need from the previous codes,
#as Robot_forward() and Robot_stop()


def moves(any, any2):
    #wait for the graph to appear on the screen
    time.sleep(3)
    
    Robot_forward(1700,1300)
    time.sleep(5)
    Robot_right()
    time.sleep(1.2)
    Robot_forward(1700,1300)
    time.sleep(5)
    Robot_stop()
if __name__ == "__main__":
    
    #create a thread to call this function
    movementThread = threading.Thread(target = moves, args = ('anything','anything2'))

    #start the thread
    movementThread.start()

    #Create an animation to plot the data, during 1 minute
    simulation = animation.FuncAnimation(fig=plotData.f0, func=loopData,
                        blit=False, frames=200, interval=20, repeat=False)

    #plotting
    plt.show()
    print('terminou')
    plt.close()

    #stop the raspberry pi
    raspi.stop()
