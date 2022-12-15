import RPi.GPIO as GPIO # import GPIO library
import time
from enum import Enum
from threading import Thread

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

camMot0 = 22
camMot1 = 23
camMot2 = 24
camMot3 = 25
cameraMotor = [camMot0, camMot1, camMot2, camMot3]

GPIO.setup(camMot0,GPIO.OUT)
GPIO.setup(camMot1,GPIO.OUT)
GPIO.setup(camMot2,GPIO.OUT)
GPIO.setup(camMot3,GPIO.OUT)

clockwiseSeq = ["0001", "0011", "0010", "0110", "0100", "1100", "1000", "1001"];
counterClockwiseSeq = ["0001", "1001", "1000", "1100", "0100", "0110", "0010", "0011"];

MotorRB = 16
MotorRE = 12 #modulated

MotorLB = 06
MotorLE = 13 #modulated

ECHO    = 17
TRIGGER = 27

Direction = Enum('Direction', 'LEFT RIGHT FORWARD BACKWARD STOP')

GPIO.setup(TRIGGER,GPIO.OUT)
GPIO.setup(ECHO, GPIO.OUT)
GPIO.output(ECHO, GPIO.LOW)
GPIO.setup(ECHO,GPIO.IN)

GPIO.setup(MotorRB,GPIO.OUT)
GPIO.setup(MotorRE,GPIO.OUT)
GPIO.output(MotorRB,GPIO.HIGH)
GPIO.output(MotorRE,GPIO.HIGH)

GPIO.setup(MotorLB,GPIO.OUT)
GPIO.setup(MotorLE,GPIO.OUT)
GPIO.output(MotorLB,GPIO.HIGH)
GPIO.output(MotorLE,GPIO.HIGH)

prawy=GPIO.PWM(MotorRE,50) # configuring Enable pin means GPIO-04 for PWM with this freq
lewy=GPIO.PWM(MotorLE,50) # configuring Enable pin means GPIO-04 for PWM with this freq
prawy.start(100) # starting it with 100% dutycycle
lewy.start(100) # starting it with 100% dutycycle

MonitorDistance=True
StopMoving=False

def Measure():
	start = 0
	stop = 0
	realstart = 0
	realstart = time.time()
	GPIO.output(TRIGGER, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(TRIGGER, GPIO.LOW)
	start = time.time()
	while GPIO.input(ECHO)==0:
		start = time.time()
		Dif = time.time() - realstart
		if Dif > 0.2:
			#print("Ultrasonic Sensor Timed out, Restarting.")
			time.sleep(0.4)
			return 0;
	while GPIO.input(ECHO)==1:
		stop = time.time()
	elapsed = stop-start
	distance = (elapsed * 36000)/2

	return distance

def showDistance(printDistance):
    Distance = Measure()
    if printDistance:
        print "Distance: " + str(Distance)
    return Distance;

def startMonitoringDistance():
    global MonitorDistance
    global StopMoving
    while MonitorDistance:
        dist = showDistance(False)
        if dist < 5 :
            print "Stop engines!"
            StopMoving=True
        time.sleep(0.1)
    return;

def setPins( pins, motorpin ):
    if len(pins) != 4:
        return "Ivalid parametr. Expected 4 chars string, got: " + setPins
    i = 0;
    for newstate in pins:
        if (newstate == '0'):
            GPIO.output(motorpin[i],GPIO.LOW)
        if (newstate == '1'):
            GPIO.output(motorpin[i],GPIO.HIGH)
        i = i + 1;
    return;

def rotateCameraClockwise( speed, motor ):
    for sequence in clockwiseSeq:
        setPins( sequence, motor );
        time.sleep(float(1) / speed);
    return;

def rotateCameraCounterClockwise ( speed, motor ):
    for sequence in counterClockwiseSeq:
        setPins( sequence, motor );
        time.sleep(float(1) / speed)
    return

def turnCameraLeft(steps):
    print "turning camera left " + str(steps) + " step"
    for i in range(1, steps):
        rotateCameraCounterClockwise( 400, cameraMotor );
    return;

def turnCameraRight(steps):
    print "turning camera right " + str(steps) + " step"
    for i in range(1, steps):
        rotateCameraClockwise( 400, cameraMotor );
    return;

def setEngines(MoveDirection, speed):
    if MoveDirection == Direction.STOP:
        print "stopping engines..."
        prawy.ChangeDutyCycle(100)
        lewy.ChangeDutyCycle(100)        
        GPIO.output(MotorRB,GPIO.HIGH)
        GPIO.output(MotorRE,GPIO.HIGH)
        GPIO.output(MotorLE,GPIO.HIGH)
        GPIO.output(MotorLB,GPIO.HIGH)
    if MoveDirection == Direction.LEFT:
        print "go " + str(MoveDirection)
        prawy.ChangeDutyCycle(speed)
        lewy.ChangeDutyCycle(100-speed)
        GPIO.output(MotorRB,GPIO.LOW)
        GPIO.output(MotorRE,GPIO.HIGH)
        GPIO.output(MotorLE,GPIO.LOW)
        GPIO.output(MotorLB,GPIO.HIGH)
    if MoveDirection == Direction.RIGHT:
        print "go " + str(MoveDirection)
        prawy.ChangeDutyCycle(100-speed)
        lewy.ChangeDutyCycle(speed)
        GPIO.output(MotorRB,GPIO.HIGH)
        GPIO.output(MotorRE,GPIO.LOW)
        GPIO.output(MotorLE,GPIO.HIGH)
        GPIO.output(MotorLB,GPIO.LOW)
    if MoveDirection == Direction.BACKWARD:
        print "go " + str(MoveDirection)
        prawy.ChangeDutyCycle(100-speed)
        lewy.ChangeDutyCycle(100-speed)
        GPIO.output(MotorRB,GPIO.HIGH)
        GPIO.output(MotorRE,GPIO.LOW)
        GPIO.output(MotorLE,GPIO.LOW)
        GPIO.output(MotorLB,GPIO.HIGH)
    if MoveDirection == Direction.FORWARD:
        print "go " + str(MoveDirection)
        prawy.ChangeDutyCycle(speed)
        lewy.ChangeDutyCycle(speed)        
        GPIO.output(MotorRB,GPIO.LOW)
        GPIO.output(MotorRE,GPIO.HIGH)
        GPIO.output(MotorLE,GPIO.HIGH)
        GPIO.output(MotorLB,GPIO.LOW)

def startMoving(speed, direction):
    global StopMoving
    if StopMoving != True:
        print ("Move " + str(direction) + " with " + str(speed) + " percent" + ", stopping: " + str(StopMoving))
        setEngines(direction, speed)
    else:
        stopEngines()

def stopEngines():
    print "Now stop"
    setEngines(Direction.STOP, 0)

def stopPWM():
    prawy.stop() # stop PWM from GPIO output; it is necessary
    lewy.stop() # stop PWM from GPIO output; it is necessary

def piruet(direction):
    global StopMoving
    print "Piruet " + str(direction)
    for speed in ([50, 50, 60, 60, 60, 60, 70, 70, 70, 70, 65, 65, 60, 60, 60, 50, 45, 45, 40, 40]):
        if (StopMoving == False):
            startMoving(speed, direction)
            time.sleep(0.5)
    stopEngines()

def go(direction, time, speed):
    print "Go " + str(direction)
    startMoving(speed, direction)
    time.sleep(time)
    stopEngines()

def countDown():
    for i in range(5,1,-1):
        print "starting in " + str(i) + "seconds..."
        time.sleep(1)

def cameraLookAround():
    for i in range(1,3):
        turnCameraLeft(140)
        turnCameraRight(140)

def Main():
    global MonitorDistance
    MonitorDistance = True
    stopEngines()

    countDown()

    distanceMonitor = Thread(target = startMonitoringDistance, args = [])
    distanceMonitor.start()

    piruet(Direction.LEFT)

    cameraLookAround()

    MonitorDistance=False
    stopPWM()
    GPIO.cleanup()

Main()
