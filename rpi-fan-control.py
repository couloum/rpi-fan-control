#!/usr/bin/env python3

import RPi.GPIO as GPIO
import sys
import os
import time

_settings = dict()
_settings_var = ["pin", "high_temp", "low_temp"]

_fan_flag = GPIO.HIGH

PROG_NAME="rpi-control-fan"
PROG_VERSION="1.0.0"

def check_env_vars():
    """
    Check that environment variables are correctly set:
      - RPI_CF_PIN
      - RPI_CF_HIGH_TEMP
      - RPI_CF_LOW_TEMP
    """

    for var in _settings_var:
        env_var = "RPI_CF_%s" % (str.upper(var))
        try:
            int(os.environ.get(env_var))
        except:
            print("Error: you must set environment variable %s to an integer value. Provided value = %s" % (env_var, os.environ.get(env_var)), file=sys.stderr)
            sys.exit(1)


    # Ensure that LOW_TEMP is lether than HIGH_TEMP
    if os.environ.get("RPI_CF_LOW_TEMP") >= os.environ.get("RPI_CF_HIGH_TEMP"):
        print("Error: RPI_CF_LOW_TEMP (%s) must be lower than RPI_CF_HIGH_TEMP (%s)" % (os.environ.get("RPI_CF_LOW_TEMP"), os.environ.get("RPI_CF_HIGH_TEMP")), file=sys.stderr)
        sys.exit(1)

def get_settings():
    for var in _settings_var:
        _settings[var] = int(os.environ.get("RPI_CF_%s" % (str.upper(var))))
    

#initialize GPIO settings
def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(_settings["pin"], GPIO.OUT)
    startFan()
    GPIO.setwarnings(False)

def startFan():
    global _fan_flag
    _fan_flag = GPIO.HIGH
    print("Starting Fan")
    GPIO.output(_settings["pin"], _fan_flag)

def stopFan():
    global _fan_flag
    _fan_flag = GPIO.LOW
    print("Stopping Fan")
    GPIO.output(_settings["pin"], _fan_flag)

def checkTemperature():
    while True:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = float(f.read().strip()) / 1000

        print("Temperature = %.2f / Fan Status = %s / high_temp: %d / low_temp: %d" % \
                (temp, _fan_flag, _settings["high_temp"], _settings["low_temp"]))
        if temp >= _settings["high_temp"] and _fan_flag != GPIO.HIGH:
            startFan()
        elif temp < _settings["low_temp"] and _fan_flag != GPIO.LOW:
            stopFan()

        time.sleep(5)


if __name__ == "__main__":
    check_env_vars()
    get_settings()

    print("Starting %s %s" % (PROG_NAME, PROG_VERSION))
    print("With settings:")
    for var in _settings_var:
        print("- %s = %s" % (var, _settings[var]))

    init()
    time.sleep(5)
    try:
        while True:
            checkTemperature()
    finally:
        GPIO.cleanup()
