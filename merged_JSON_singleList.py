# Output looks like this:
#
#    A B STATE SEQ DELTA SWITCH
#    1 1   3    2    1    0
#    0 1   2    3    1    0
#    0 0   0    0    1    0
#    1 0   1    1    1    0
#    1 1   3    2    1    0
#    0 1   2    3    1    0

# Parses the output of iwlist scan into a table

import math
import datetime
import RPi.GPIO as GPIO

import sys
import subprocess

import json


interface = "wlan0"

# Switch button parameters
startPin = 22
stopPin = 24
ledpin = 17
# Rotary encoder parameters
A_PIN  = 8 
B_PIN  = 7

GPIO.setmode(GPIO.BCM)

#set channels as input or output
GPIO.setup(startPin,GPIO.IN)
GPIO.setup(stopPin,GPIO.IN)
GPIO.setup(A_PIN,GPIO.IN)
GPIO.setup(B_PIN,GPIO.IN)

GPIO.setup(ledpin,GPIO.OUT)
GPIO.output(ledpin,True)    # initially LED is turned off as pin is high


PERIMETER = 49.951  # perimeter in cm - verified


# You can add or change the functions to parse the properties of each AP (cell)
# below. They take one argument, the bunch of text describing one cell in iwlist
# scan and return a property of that cell.

# code outputs the same thing as typing "iwlist wlan0 scan" in the command line
def get_name(cell):
    return matching_line(cell,"ESSID:")[1:-1]

def get_quality(cell):
    quality = matching_line(cell,"Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3) + " %"

def get_channel(cell):
    return matching_line(cell,"Channel:")

def get_signal_level(cell):
    # Signal level is on same line as Quality data so a bit of ugly
    # hacking needed...
    sig = matching_line(cell,"Quality=").split("Signal level=")[1]
    sep = " "
    return sig.split(sep,1)[0]


def get_encryption(cell):
    enc=""
    if matching_line(cell,"Encryption key:") == "off":
        enc="Open"
    else:
        for line in cell:
            matching = match(line,"IE:")
            if matching!=None:
                wpa=match(matching,"WPA Version ")
                if wpa!=None:
                    enc="WPA v."+wpa
        if enc=="":
            enc="WEP"
    return enc

def get_address(cell):
    return matching_line(cell,"Address: ")

# Here's a dictionary of rules that will be applied to the description of each
# cell. The key will be the name of the column in the table. The value is a
# function defined above.

rules={"Name":get_name,
        "Quality":get_quality,
        "Channel":get_channel,
        "Encryption":get_encryption,
        "Address":get_address,
        "Signal(dBm)":get_signal_level
        }

# Here you can choose the way of sorting the table. sortby should be a key of
# the dictionary rules.

def sort_cells(cells):
    sortby = "Quality"
    reverse = True
    cells.sort(None, lambda el:el[sortby], reverse)

# You can choose which columns to display here, and most importantly in what order. Of
# course, they must exist as keys in the dict rules.

columns=["Name","Address","Quality","Signal(dBm)", "Channel","Encryption"]




# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching=match(line,keyword)
        if matching!=None:
            return matching
    return None

def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
        returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None

def parse_cell(cell):
    """Applies the rules to the bunch of text describing a cell and returns the
        corresponding dictionary"""
    parsed_cell={}	# dictionary
    for key in rules:
        rule=rules[key]		# rule = "Imperial - WPA" for example if key = "Name"
        parsed_cell.update({key:rule(cell)})
    return parsed_cell


def cells_fn():
    cells=[[]] # a list of lists
    
    proc = subprocess.Popen(["iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True) # runs "iwlist wlan0 scan" on command line and "pipes out" its output to this Python programme
    out, err = proc.communicate() # the above line specified what function to run and its parameters. This line actually sends that data to the standard input channel of the process one time
    # above line: proc.communicate returns two arguments, assigned to out and err respectively
    # return statement of proc.communicate looks like: "return first_name, last_name"
    
    for line in out.split("\n"): # split out into list of strings that were orginally separated by \n
        cell_line = match(line,"Cell ")
        if cell_line != None:
            cells.append([])
            line = cell_line[-27:] # not sure why it is -27
        cells[-1].append(line.rstrip()) # adding new line (list) as part of cells (list of lists)
    
    cells=cells[1:]

    parsed_cells=[]

    for cell in cells:
        parsed_cells.append(parse_cell(cell)) #list of parse_cell(cell) outputs
        
    sort_cells(parsed_cells)

    table=[columns]
    for cell2 in parsed_cells:
        cell_properties=[]
        if cell2["Name"] == "Imperial-WPA":
            for column in columns:
                cell_properties.append(cell2[column])
        else:
            continue
        table.append(cell_properties)
   

    widths=map(max,map(lambda l:map(len,l),zip(*table))) #functional magic

    justified_table = []
    for line2 in table:
        justified_line=[]
        for i,el in enumerate(line2):
            justified_line.append(el.ljust(widths[i]+2))
        justified_table.append(justified_line)

    return justified_table



try:
    while True:
        if (GPIO.input(startPin)):

            print "Start button has been pressed!\n"
            
            # open the file
            t = datetime.datetime.now()
            filename = "/home/pi/readings/EveryChangeinLength_JSON/" + t.strftime("%Y-%m-%d_%H-%M-%S") + ".json"

            print("\nA\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\t%s\t%s\t%s\t%s\t%s\t%s\n" %(columns[0], columns[1], columns[2], columns[3], columns[4], columns[5]))

            # read in pins A and B to set the initial variables
            last_a_state = GPIO.input(A_PIN)
            last_b_state = GPIO.input(B_PIN)
            
            # set initial values
            last_heading = 0
            accumulated_delta = 0
            last_delta = 0
            last_sequence = (last_a_state ^ last_b_state) | last_b_state << 1
            delta = 0
            length = 0

            lengthset = []
            timeset = []
            wifi0 = []
            wifi1 = []
            wifi2 = []
            wifi3 = []
            wifi4 = []
            wifi5 = []
        
            while True:
                GPIO.output(ledpin,False)   # LED turns on
    
                # prints the heading after every 20 lines
                if (last_heading != 0) and ((last_heading % 20) == 0):
                    print("\nA\tB\tLAST_A\tLAST_B\tSEQ\tL_SEQ\tDELTA\tACC_DELTA\tLENGTH(cm)\tTIME\t%s\t%s\t%s\t%s\t%s\t%s\n" %(columns[0], columns[1], columns[2], columns[3], columns[4], columns[5]))

                # extract individual signal bits for A and B
                a_state = GPIO.input(A_PIN)
                b_state = GPIO.input(B_PIN)
            
                
                # determine the delta value and add it if either A or B has changed
                if((last_a_state != a_state) or (last_b_state != b_state)):
                    sequence = (a_state ^ b_state) | (b_state << 1) 

                    # compute delta:
                    # This is the same as the value returned by encoder.get_delta()
                    delta = (sequence - last_sequence) % 4
                    if delta==3:
                        delta=-1
                    elif delta==2:
                        # this is an attempt to make sense out of a missed step:
                        # assume that we have moved two steps in the same direction
                        # that we were previously moving.
                        delta = int(math.copysign(delta, last_delta))

                    accumulated_delta = accumulated_delta+delta

                    length = (accumulated_delta/20.0)*PERIMETER    # there are 5 pulses in 1/4 turn of the surveyor's wheel, delta = 1 maeans 1/4 turn has been completed
                    # error = +/- 49.951/20 = +/- 2.50cm 
                    t = datetime.datetime.now()
                    timestamp = t.strftime("%H:%M:%S.%f")

                    justified_table_final = cells_fn()
                    wifi_string = ""
                    wifiset = []
                    
                    
                    count =  0
                    for line in justified_table_final:
                        if count % 2 != 0:
                            for el in line:
                                wifi_string = wifi_string + el + "\t"
                                el = el.rstrip()
                                wifiset.append(el)
                            
                            final_str = '%1d\t%1d\t%1d\t%1d\t%4d\t%4d\t%4d\t%4d\t\t%.2f\t%s\t%s\n' % (a_state, b_state, last_a_state, last_b_state, sequence, last_sequence, delta, accumulated_delta, length, timestamp, wifi_string)
                            
                            print "%s\n" % final_str
                            wifi_string = ""
                            
                            lengthset.append(length)
                            timeset.append(timestamp)
                            wifi0.append(wifiset[0])
                            wifi1.append(wifiset[1])
                            wifi2.append(wifiset[2])
                            wifi3.append(int(wifiset[3])) #convert signal strength to int
                            wifi4.append(wifiset[4])
                            wifi5.append(wifiset[5])
                            
                            wifiset = []
                            
                        count = count + 1
                    
                    last_heading += 1
                    last_a_state = a_state
                    last_delta = delta
                    last_b_state = b_state
                    last_sequence = sequence

                if (GPIO.input(stopPin)):
                    print "Stop button has been pressed!\n"
                    GPIO.output(ledpin,True)    #LED turns off
                    
                    data = {
                            'length(cm)' : lengthset,
                            'time' : timeset,
                            columns[0] : wifi0,
                            columns[1] : wifi1,
                            columns[2] : wifi2,
                            columns[3] : wifi3,
                            columns[4] : wifi4,
                            columns[5] : wifi5
                            }
                    
                    with open(filename,"w+") as f:
                        json.dump(data, f)
                    print "New file %s has been written.\n" % filename
                    #set all values to the initial state
                    delta = 0
                    accumulated_delta = 0
                    length = 0
                    last_heading = 0
                    count = 0
                    break


finally:
    print "Exiting program!\n"
    GPIO.cleanup()  # resets all input/output configurations










