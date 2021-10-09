import busio
import digitalio
import board
import threading
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# global variables
spi = None
cs = None
mcp = None
chan1 = None
chan2 = None
switch = 17

# creates the spi bus
def createSPIBus():
    return busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# creates the cs (chip select)
def createChipset():
    return digitalio.DigitalInOut(board.D5)

# creates the mcp object
def createMCP():
    return MCP.MCP3008(createSPIBus(), createChipset())

def createAnalogInput():
    temp = AnalogIn(createMCP(), MCP.P1)
    ldr = AnalogIn(createMCP(), MCP.P2)
    return temp, ldr

def callback_method():
    print("falling edge detected on pin 17")

def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # If your pin is set to use pull up resistors
    # Connect a button between <channel> and GND
    GPIO.add_event_detect(switch, GPIO.FALLING, callback=callback_function(), bounceTime=200)

def exit():
    GPIO.cleanup()

# Converts the adc value to temperature in degrees celcius
def convert_to_temperature(analogIn):
    millivolts = analogIn.value * (analogIn.reference_voltage * 1000/65535)
    return (millivolts - 500) / 10

# Makes use of a thread that prints results every 10 seconds
def print_results():
    start = time.time()
    thread = threading.Timer(10.0, print_results)
    thread.daemon = True    # Daemon threads exit when the program does
    thread.start()

    end = time.time()
    temp, ldr = createAnalogInput()
    print(f"{10 - ((end - start)%10)}\t <{temp.value}>\t <{convert_to_temperature()}> C\t <{ldr.value}>")



if __name__ == "__main__":
    print("Runtime\t Temp Reading\t Temp\t Light Reading.")
    print_results()