import rotationSpeed_Graph
import time
import pigpio
import pid_controller
from hcsr06sensor import HCSR04

samples = 5
sensor = HCSR04(7, 12)


raspi = pigpio.pi()
def path1():
   time.sleep(1)
   pid_controller.straight(1.1)
   time.sleep(1)
   pid_controller.right(0.25)
   pid_controller.straight(1)
   time.sleep(1)
   pid_controller.left(0.25)
   pid_controller.straight(1)
   time.sleep(1)
   pid_controller.straight(2)
   time.sleep(1)
   pid_controller.left(0.25)
   pid_controller.straight(1)
   time.sleep(1)
   pid_controller.right(0.25)
   pid_controller.straight(1)
   time.sleep(1)
   pid_controller.straight(1.5)

def path2():
    time.sleep(1)
    pid_controller.straight(1)
    time.sleep(1)
    pid_controller.left(1)
    pid_controller.straight(1)
    time.sleep(1)
    pid_controller.right(0.12)
    pid_controller.straight(2.5)
    time.sleep(1)
    pid_controller.left(0.5)
    pid_controller.straight(1)
    time.sleep(1)
    pid_controller.right(0.5)
    pid_controller.straight(2)
    time.sleep(1)
    
def hcsr():
    while True:
        s = time.time()
        distance = sensor.measure(samples, "cm")
        e = time.time()
        print("Distance:", distance, "cm")
        print("Used time:", (e - s), "seconds")
        if distance < 5 :
            pid_controller.right(0.5)
            pid_controller.straight(1.5)
            time.sleep(1)
        time.sleep(0.01)
    sensorThread = threading.Thread(target=Sonar, args=(sensor, samples))
    sensorThread.start()
def main():
    hcsr()

if __name__ == "__main__":
    main()