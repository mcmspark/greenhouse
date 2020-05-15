# greenhouse
a raspberry pi project with e-Ink display that employs 3 Ic2 sensors to monitor my greenhouse

![alt text](https://raw.githubusercontent.com/mcmspark/greenhouse/master/currentDisplay.png)

The display includes, Temperature, Humitity, Lux, and Pressure graph.  It also includes Wifi Strength and battery Level, as well as the date time the display was updated (since e-ink does not require power to run)

[Powered by Solar Cell](https://www.amazon.com/gp/product/B01MCXZJ8Y/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1) and 
[Packaged in waterproof case](https://www.amazon.com/gp/product/B07C97HXX8/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)

## dependancies
This Python display is for the [Pimeroni Inky pHAT](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat)
It also uses 3 Adafruit sensors
- [BME280 Temperature, Pressure Humidity sensor](https://www.adafruit.com/product/2652)
- [VEML7700 Lux sensor](https://www.adafruit.com/product/4162)
- [ADS1015 12bit ADC](https://www.adafruit.com/product/1083)

Install Python Libraries
```
sudo pip3 install inky
pip3 install RPI.GPIO
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-veml7700
sudo pip3 install adafruit-circuitpython-ads1x15
```

## improvements
I followed [this guide](https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy) to reduce power consumption on the Pi Zero W
```
/usr/bin/tvservice -o
echo none | sudo tee /sys/class/leds/led0/trigger
echo 1 | sudo tee /sys/class/leds/led0/brightness
```

I also [diabled bluetooth](https://scribles.net/disabling-bluetooth-on-raspberry-pi/)


