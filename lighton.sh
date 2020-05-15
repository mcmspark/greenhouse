#!/bin/sh
echo cpu0 | sudo tee /sys/class/leds/led0/trigger
echo 0 | sudo tee /sys/class/leds/led0/brightness

