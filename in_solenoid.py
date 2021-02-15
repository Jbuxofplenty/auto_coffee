#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys
import argparse
import signal

parser = argparse.ArgumentParser(description='Take in time for solenoid.')
parser.add_argument('--time', required=True,
                    help='Time to turn solenoid on.')

args = parser.parse_args()
TEST_OUT = 19

def signal_handler(sig, frame):
    GPIO.output(TEST_OUT, GPIO.LOW)
    GPIO.cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_OUT, GPIO.OUT)

GPIO.output(TEST_OUT, GPIO.LOW)
GPIO.output(TEST_OUT, GPIO.HIGH)
print('Turned on solenoid.')
time.sleep(int(args.time))
GPIO.output(TEST_OUT, GPIO.LOW)
print('Turned off solenoid.')
GPIO.cleanup()
sys.exit()
