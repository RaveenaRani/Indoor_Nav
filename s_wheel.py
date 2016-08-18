# Sample code for both the RotaryEncoder class and the Switch class.
# The common pin for the encoder should be wired to ground.
# The sw_pin should be shorted to ground by the switch.

# Output looks like this:
#
#    A B STATE SEQ DELTA SWITCH
#    1 1   3    2    1    0
#    0 1   2    3    1    0
#    0 0   0    0    1    0
#    1 0   1    1    1    0
#    1 1   3    2    1    0
#    0 1   2    3    1    0

import math
import datetime
import RPi.GPIO as GPIO

# Switch button parameters
startPin = 22
stopPin = 24
ledpin = 17
GPIO.setmode(GPIO.BCM)

#set channels as input or output
GPIO.setup(startPin,GPIO.IN)
GPIO.setup(stopPin,GPIO.IN)
GPIO.setup(ledpin,GPIO.OUT)
GPIO.output(ledpin,True)

# Rotary encoder and wheel parameters
A_PIN  = 8  # was previously 10
B_PIN  = 7  # was previously 11

GPIO.setup(A_PIN,GPIO.IN)
GPIO.setup(B_PIN,GPIO.IN)

PERIMETER = 49.951  # perimeter in cm - verified

# NOTE: the library includes individual calls to get
# the rotation_state, rotation_sequence and delta values.  
# However this demo only reads the rotation_state and locally
# derives the rotation_sequence and delta.  This ensures that
# the derived values are based on the same two input bits A and B.
# If we used the library calls, there is a very real chance that
# the inputs would change while we were sampling, giving us 
# inconsistent values in the output table.


try:
    while True:
        if (GPIO.input(startPin)):

            print "Start button has been pressed!\n"
            
            # open the file
            t = datetime.datetime.now()
            filename = "/home/pi/readings/" + t.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            f = open(filename,"w+")

            f.write("A\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\n")

            print "New file %s has been created.\n" % filename

            print("\nA\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\n")

            last_a_state = GPIO.input(A_PIN)
            last_b_state = GPIO.input(B_PIN)
            last_heading = 0
            accumulated_delta = 0
            last_delta = 0
            last_sequence = (last_a_state ^ last_b_state) | last_b_state << 1
 
            delta = 0
            length = 0
            
            while True:
                GPIO.output(ledpin,False)
                
                # print a heading every 20 lines
                if (last_heading != 0) and (last_heading % 20) == 0:
                    f.write("\nA\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\n")
                    print("\nA\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\n")

                # extract individual signal bits for A and B
                a_state = GPIO.input(A_PIN)
                b_state = GPIO.input(B_PIN)

                if((last_a_state != a_state) or (last_b_state != b_state)):
                    sequence = (a_state ^ b_state) | (b_state << 1) 

                    # compute delta:
                    # This is the same as the value returned by encoder.get_delta()
                    delta = (sequence - last_sequence) % 4
                    if delta == 3:
                        delta = -1
                    elif delta==2:
                        # this is an attempt to make sense out of a missed step:
                        # assume that we have moved two steps in the same direction
                        # that we were previously moving.
                        delta = int(math.copysign(delta, last_delta))

                    accumulated_delta = accumulated_delta+delta

                    length = (accumulated_delta/20.0)*PERIMETER    # there are 5 pulses in 1/4 turn of the surveyor's wheel, delta = 1 maeans 1/4 turn has been completed
                    t = datetime.datetime.now()
                    timestamp = t.strftime("%H:%M:%S.%f")
                    final_str = '%1d\t%1d\t%1d\t%1d\t%4d\t%4d\t%4d\t%4d\t\t%.2f\t%s\n' % (a_state, b_state, last_a_state, last_b_state, sequence, last_sequence, delta, accumulated_delta, length, timestamp)
                    f.write(final_str)
                    print "%s\n" % final_str
                    last_heading += 1
                    last_a_state = a_state
                    last_b_state = b_state
                    last_sequence = sequence


                if (GPIO.input(stopPin)):
                    print "Stop button has been pressed!\n"
                    GPIO.output(ledpin,True)
                    f.close()
                    delta = 0
                    accumulated_delta = 0
                    length = 0
                    last_heading = 0
                    break


finally:
    print "Exiting program!\n"
    GPIO.cleanup()





