# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    pass


# Setup Pins
def setup():

    global pwm_LED, pwm_Buzzer

    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    # Setup regular GPIO
    GPIO.setup(LED_value, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)

    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(buzzer, GPIO.OUT)

    # Setup PWM channels
    pwm_LED = GPIO.PWM(LED_accuracy, 10)  # OR 1000
    pwm_LED.start(0)
    pwm_Buzzer = GPIO.PWM(buzzer, 10)
    pwm_Buzzer.start(50)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.RISING, callbacks=callback_function, bouncetime=295)
    #GPIO.add_event_detect(btn_submit, GPIO.FALLING, callbacks=callback_function, bouncetime=295)
    GPIO.add_event_detect(btn_increase, GPIO.RISING, callbacks=callback_function, bouncetime=295)
    #GPIO.add_event_detect(btn_increase, GPIO.FALLING, callbacks=callback_function, bouncetime=295)


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    # Get the scores
    global scores = []
    for i in range(score_count):
        scores.append(['name', 0])
        letters = ""
        for j in range(3):
            letters += chr(eeprom.read_byte(4 + i*4 + j))
        scores[i][0] = letters
        scores[i][1] = eeprom.read_byte((i*4 + 3) + 4)

    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():

    user_name = input("Enter your name: ")
    if len(user_name) > 3:
        user_name = user_name[:3]
    
    # fetch scores
    score_count, new_arr = fetch_scores()
    score_count = score_count + 1

    # include new score
    new_arr.append(["name", 0])
    new_arr[score_count - 1][0] = user_name
    new_arr[score_count - 1][1] = attempts  

    # sort
    new_arr.sort(key=lambda x: x[1])

    # update total amount of scores
    eeprom.write_byte(0, score_count)
   
    # write new scores
    new_arr_write = []
    for content in new_arr:
        for y in content[0]:
            new_arr_write.append(ord(y))
        new_arr_write.append(content[1])
        eeprom.write_block(1, new_arr_write)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global guess
    global attempts

    attempts = attempts + 1
    LED_update()   
    guess += 1
    if guess == 8:
        guess = 0
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    led_inp = (8 - guess)/(8 - value)*100
    if (8 - guess) > (8 - value):
        led_inp = 15
    
    pwm_LED.ChangeDutyCycle(led_inp)
    GPIO.output(LED_accuracy, True)
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass

def LED_update():
    if guess == 0:
        GPIO.output(LED_value, False)
    elif guess == 1:
        GPIO.output([11, 13], False)
        GPIO.output(15, True)
    elif guess == 2:
        GPIO.output([11, 15], False)
        GPIO.output(13, True)
    elif guess == 3:
        GPIO.output(11, False)
        GPIO.output([13, 15], True)
    elif guess == 4:
        GPIO.output(11, True)
        GPIO.output([13, 15], False)
    elif guess == 5:
        GPIO.output([11, 15], True)
        GPIO.output(13, False)
    elif guess == 6:
        GPIO.output([11, 13], True)
        GPIO.output(15, False)
    elif guess == 7:
        GPIO.output(LED_value, True)


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
