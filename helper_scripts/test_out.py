#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys

TEST_OUT = 20
TEST_OUT_1 = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_OUT, GPIO.OUT)
GPIO.setup(TEST_OUT_1, GPIO.OUT)

high = True

while True:
    try:
        time.sleep(2)
        if high:
            GPIO.output(TEST_OUT, GPIO.LOW)
            GPIO.output(TEST_OUT_1, GPIO.LOW)
            high = False
            print('high')
        else:
            GPIO.output(TEST_OUT, GPIO.HIGH)
            GPIO.output(TEST_OUT_1, GPIO.HIGH)
            high = True
            print('low')


    except KeyboardInterrupt:
        print ('\ncaught keyboard interrupt!, bye')
        GPIO.cleanup()
        sys.exit()
