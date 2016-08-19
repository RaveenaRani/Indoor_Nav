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
GPIO.output(ledpin,True)

startPin = 22
stopPin = 24
GPIO.setup(startPin,GPIO.IN)
GPIO.setup(stopPin,GPIO.IN)


while True:
    if (GPIO.input(startPin)):

        print "Start pin has been pressed\n"

        for i in range(0,50):

            blink(ledpin)
            print "i is %d\n" %(i)

            if (GPIO.input(stopPin)):
                GPIO.output(ledpin,True)
                print "STop pin has been pressed\n"
                i = 0
                GPIO.cleanup()
                break
