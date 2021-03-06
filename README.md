# greenhouse
a raspberry pi project with e-Ink display that employs 3 Ic2 sensors to monitor my greenhouse
![running in the greenhouse](https://raw.githubusercontent.com/mcmspark/greenhouse/master/image3.jpg)
![e-ink display](https://raw.githubusercontent.com/mcmspark/greenhouse/master/currentDisplay.png)

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
I wanted to echo the display on the InkyPhat to a webpage
It was not clear in the Pimeroni docs, but adding a pallate I was able to output the image to both the display and to a file.
```
inky_display.set_image(img)
inky_display.show()
img.putpalette([255,255,255,0,0,0,255,0,0])
img.save("currentDisplay.png")
```

Route port 80 to port 8080 (add this to /etc/rc.local)
```
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j REDIRECT --to-port 8080
```

I followed [this guide](https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy) to reduce power consumption on the Pi Zero W
```
/usr/bin/tvservice -o
echo none | sudo tee /sys/class/leds/led0/trigger
echo 1 | sudo tee /sys/class/leds/led0/brightness
```
I found that I can save another 20 to 25 mA by disabling the Wifi.
I implemented 2 different stategies to decide when to keep the Wifi on or off.
1) Wifi Power Schedule (Wifi is on at the top 20 min of every hour and off all night)
2) Lux triggered Wifi (Wifi is on only in the Day)

I also [diabled bluetooth](https://scribles.net/disabling-bluetooth-on-raspberry-pi/)
```
sudo nano /boot/config.txt
```
Add below, save and close the file.
```
# Disable Bluetooth
dtoverlay=pi3-disable-bt
```
Disable related services.
```
sudo systemctl disable hciuart.service
sudo systemctl disable bluealsa.service
sudo systemctl disable bluetooth.service
```

## power
I scavenged a charge/regulator from a USB powerbank
![USB regulator](https://raw.githubusercontent.com/mcmspark/greenhouse/master/image2.jpg)
and hooked it to 2 3.7v Lithium cells in parallel ([18650](https://www.18650batterystore.com/18650-p/samsung-25r-18650.htm))

On sunny days the solar cell fully charges the batteries, but in the spring and fall I sometimes have to charge it.

To find the range of battery voltages I charged the battery untill it stopped rising.  Then I rand the unit with no charging until it died.

From this I used 3.2v as 0%
and 4.096v as 100% (WRONG)

Little did I know the ADS1015 default gain can only measure a max of 4.096.
after setting the gain to 2/3 (I know right)
The new max voltage is 4.1612v

From the datasheet:
<table>
<tr><td>Table 3. PGA Gain Full-Scale Range</td></tr>
  <tr><td>PGA SETTING</td><td>FS(V)</td></tr>
  <tr><td>2/3</td><td>±6.144V(1)</td></tr>
  <tr><td>1</td><td>±4.096V(1)</td></tr>
  <tr><td>2</td><td>±2.048V</td></tr>
  <tr><td>4</td><td>±1.024V</td></tr>
  <tr><td>8</td><td>±0.512V</td></tr>
  <tr><td>16</td><td>±0.256V</td></tr>
</table>

## running
Edit /etc/rc.local and add
```
/usr/bin/tvservice -o

cd /home/pi/GreenHouse
python3 GreenHouse.py &
```
then reboot.

The display is available on the e-Ink and on a webpage on port 8080  http://greenhouse:8080

