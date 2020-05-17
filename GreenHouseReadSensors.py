import subprocess
import time
import iwlist
from collections import namedtuple
import bme280
import board
import busio
import adafruit_veml7700
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
 
i2c = busio.I2C(board.SCL, board.SDA)
veml7700 = adafruit_veml7700.VEML7700(i2c)
ads = ADS.ADS1015(i2c)
  
def getConnectedWifi():
  cmd=["iwgetid","-a"]
  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  points = proc.stdout.read().decode('utf-8')
  parts=points.split("Cell:")
  if(len(parts)>1):
    #print(str(parts[1]))
    return str(parts[1]).replace('"','').replace('\n','').replace(' ','')
  else:
	  return ""

def getWiFiStrength():
  content=iwlist.scan(interface='wlan0')
  cells=iwlist.parse(content)
  strength = 0
  connectedwifi=getConnectedWifi()
  for cell in cells:
    if(str(cell['mac'])==connectedwifi):
      strength=int(cell["signal_quality"])*4/int(cell["signal_total"])
      break
      #print(str(cell['mac']),connectedwifi,str(cell['mac'])==connectedwifi)
  #print(strength)
  return round(strength,1)

measurement = namedtuple("measurement","time temp humid press lux batt wifi")

def tempInF(temperature):
  return temperature * 9 / 5 + 32

def getMeasurements():
  timestr=time.strftime('%I:%M%p %b %d, %Y')
  temperature,pressure,humidity = bme280.readBME280All()
  tempF =  temperature * 9 / 5 + 32
  inHg = pressure * 0.02952998751
  lux = veml7700.lux
  chan = AnalogIn(ads, ADS.P0)
  battLevel = (chan.voltage-3.4)*1000.0/7.0
  wifiStrength=getWiFiStrength()
#  4.09 = full 3.1 = empty
# print(chan.value, chan.voltage)
  return measurement(timestr, str(round(temperature,1)), str(round(humidity,1)), str(round(pressure,6)), str(round(lux,1)) if lux>100 else str(lux) , round(battLevel,1), wifiStrength)

if __name__ == '__main__':
  print(getMeasurements())
