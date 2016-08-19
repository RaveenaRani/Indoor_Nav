import RPi.GPIO as GPIO
import time

def blink(pin):
    GPIO.output(pin,True)
    time.sleep(2)
    GPIO.output(pin,False)
    time.sleep(2)
    return

GPIO.setmode(GPIO.BCM)

ledpin = 17
GPIO.setup(ledpin,GPIO.OUT)

for i in range(0,50):
    blink(ledpin)
    print "i is %d\n" %(i)

GPIO.cleanup()
