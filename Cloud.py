#### Set up GPIO
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

###########################
# Libaries
###########################

### Libraries for Ultrasonic Sensor
import time
import statistics

### Libraries for  RC522
from mfrc522 import SimpleMFRC522


### Libraries for LCD
from rpi_lcd import LCD

### Libraries for Keypad
from keypad import keypad

### Libraries for Cloud
import http.client as httplib
import urllib

###########################
# Constants
###########################

#### Constants of Ultrasonic Sensor
trigger_pin=4
echo_pin=17      
number_of_samples=5 # número de this is the number of times the sensor tests the distance and then picks the middle value to return
sample_sleep = .01  # amount of time in seconds that the system sleeps before sending another sample request to the sensor. You can try this at .05 if your measurements aren't good, or try it at 005 if you want faster sampling.
calibration1 = 30   # the distance the sensor was calibrated at
calibration2 = 1750 # the median value reported back from the sensor at 30 cm
time_out = .05 # measured in seconds in case the program gets stuck in a loop

### Constants of IR Sensor
ir_pin=27

### Constants of RC522
reader=SimpleMFRC522()
#Pin out
#3.3V pin 17 (3.3V)
#RST pin 22 (GPIO 25)
#GND pin 20 (GND)
#IRG NA
#MISO pin 21 (MISO)
#MOSI pin 19 (MOSI)
#SCK pin 23 (SCLK)
#SS pin 24 (CEO)

### Constants of LCD
lcd=LCD()

### Constants of Keypad
kp = keypad(columnCount = 3)

### Constants of Cloud
key="3LQZ57MWD2CIXY45"
###########################
# Pin set up
###########################

# Set up the pins for output and input of Ultrasonic Sensor
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Set up the pins for output and input of IR Sensor
GPIO.setup(ir_pin, GPIO.IN)

###########################
# Variables
###########################

#### initialize variables of Ultrasonic Sensor
samples_list = [] #type: list # list of data collected from sensor which are averaged for each measurement
stack = []

###########################
# Functions
###########################

#####################
### functions of Ultrasonic Sensor
def timer_call(channel) :
# call back function when the rising edge is detected on the echo pin
    now = time.monotonic()  # gets the current time with a lot of decimal places
    stack.append(now) # stores the start and end times for the distance measurement in a LIFO stack

def trigger():
    # set our trigger high, triggering a pulse to be sent - a 1/100,000 of a second pulse or 10 microseconds
    GPIO.output(trigger_pin, GPIO.HIGH) 
    time.sleep(0.00001) 
    GPIO.output(trigger_pin, GPIO.LOW)

def check_distance():
# generates an ultrasonic pulse and uses the times that are recorded on the stack to calculate the distance
    samples_list.clear()
    while len(samples_list) < number_of_samples:       # Checks if the samples_list contains the required number_of_samples
        # Tell the sensor to send out an ultrasonic pulse.
        trigger()
        # check the length of stack to see if it contains a start and end time . Wait until 2 items in the list
        while len(stack) < 2:                          # waiting for the stack to fill with a start and end time
            start = time.monotonic()                   # get the time that we enter this loop to track for timeout
            while time.monotonic() < start + time_out: # check the timeout condition
                pass
            trigger()                                  # The system timed out waiting for the echo to come back. Send a new pulse.
        if len(stack) == 2:                          # Stack has two elements on it.
            # once the stack has two elements in it, store the difference in the samples_list
            samples_list.append(stack.pop()-stack.pop())
        elif len(stack) > 2:
            # somehow we got three items on the stack, so clear the stack
            stack.clear()
        time.sleep(sample_sleep)          # Pause to make sure we don't overload the sensor with requests and allow the noise to die down
    # returns the media distance calculation
    return (statistics.median(samples_list)*1000000*calibration1/calibration2)

def check_item() :
    ### Ultrasonic
    GPIO.add_event_detect(echo_pin, GPIO.BOTH, callback=timer_call)  # add rising and falling edge detection on echo_pin (input)
    for i in range(100): # check the distance 100 times
        print(round(check_distance(), 1)) # print out the distance rounded to one decimal place
        txt= check_distance()#test cloud
        send_cloud(txt)#test cloud
    

#####################
### functions of Ir
def check_sale() :
    ###Ir
    for tempo in range(10) :
        val=GPIO.input(ir_pin)
        print(val)
        time.sleep(1)

#####################
### functions of IRF 
def write_card() :
#Writes a user name value into the IRF card
    text=input("New Data: ")# Set IRF card name
    print("place tag")
    try:
        reader.write(text) # Set IRF card name into the card
        print("written")
    finally:
        print("written")

def read_card() :    
#Reads the value of the name stored into card
    try:
        print("place tag")
        id,text=reader.read() #takes the unique id of the card and the value of the name stored into it
        # in 2 variables

    finally:
        print(id)
        print(text)

#####################
### Keypad functions
def read_keypad() :
    # waiting for a keypress
    digit = None
    while digit == None:
        digit = kp.getKey()
    # Print result
    print (digit)
    time.sleep(0.5)

    ###### 4 Digit wait ######
    cod = []
    for i in range(4):
        digit = None
        while digit == None:
            digit = kp.getKey()
        cod.append(digit)
        time.sleep(0.4)

    # Check digit code
    print(cod)
    if cod == [1, 2, 3, '#']:#select digit combination
        print ("Code accepted")

#####################
### Cloud function
def send_cloud(txt) :
    params = urllib.parse.urlencode({'field1': txt, 'key':key }) 
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print (txt)
        #print (response.status, response.reason)
        data = response.read()
        conn.close()
    except:
        print ("connection failed")


###########################
# Main Program
###########################

### functions of LCD
# lcd.text("Hola",1)
# lcd.text("Que hace",2)
# time.sleep(3)
# lcd.clear()
# read_keypad()
# check_sale()
# check_item()
# write_card()
# time.sleep(3)
# read_card()
check_item()

GPIO.cleanup()


