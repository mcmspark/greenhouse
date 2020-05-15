# greenhouse
a raspberry pi project with e-Ink display that employs 3 Ic2 sensors to monitor my greenhouse

![alt text](https://raw.githubusercontent.com/mcmspark/greenhouse/master/currentDisplay.png)

## dependancies
This Python display is for the [Pimeroni Inky pHAT](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat)
It also uses 3 Adafruit sensors
[BME280 Temperature, Pressure Humidity sensor](https://www.adafruit.com/product/2652)
[VEML7700 Lux sensor](https://www.adafruit.com/product/4162)
[ADS1015 12bit ADC](https://www.adafruit.com/product/1083)

Install Python Libraries
```
sudo pip3 install inky
pip3 install RPI.GPIO
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-veml7700
```
