import RPi.GPIO as GPIO
import time

import threading

GPIO.setmode(GPIO.BCM)

def blink(pin):
    GPIO.output(pin,True)
    time.sleep(2)
    GPIO.output(pin,False)
    time.sleep(2)
    return

def startFunc(pin):
    while(GPIO.input(pin)==0):
        if (GPIO.input(pin)):

            print "Start pin has been pressed\n"

            i=0

            stopping_thread = threading.Thread(target=stopFunc, args=(stopPin,))
            stopping_thread.start()
            
            while True:
                blink(ledpin)
                print "i is %d\n" %(i)
                i += 1

def stopFunc(pin):
    while(GPIO.input(pin)==0):
        if (GPIO.input(pin)):
            GPIO.output(ledpin,True)
            print "STop pin has been pressed\n"
            #GPIO.cleanup()
            startFunc(startPin)


ledpin = 17
GPIO.setup(ledpin,GPIO.OUT)
GPIO.output(ledpin,True)

startPin = 22
stopPin = 24
GPIO.setup(startPin,GPIO.IN)
GPIO.setup(stopPin,GPIO.IN)



startFunc(startPin)
            
