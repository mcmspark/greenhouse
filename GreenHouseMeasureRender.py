import subprocess
import time
import iwlist
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from font_hanken_grotesk import HankenGrotesk
from collections import namedtuple
import bme280
import json
import board
import busio
import adafruit_veml7700
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
 
i2c = busio.I2C(board.SCL, board.SDA)
veml7700 = adafruit_veml7700.VEML7700(i2c)
ads = ADS.ADS1015(i2c)

#print("Ambient light:", veml7700.light)
#print("Lux:", veml7700.lux)

inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.WHITE)
data = []

def turnOffTheActLight(state):
  if state :
    cmd = ["./lightoff.sh"]
  else :
    cmd = ["./lighton.sh"]
  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def drawWifi(draw,xy,strength,colorDark,colorLight):
  x=xy[0]
  y=xy[1]
  draw.rectangle(((x, y+9), (x+1, y+12)), fill = colorDark if strength>0 else colorLight)
  draw.rectangle(((x+3, y+6), (x+4, y+12)), fill = colorDark if strength>1 else colorLight)
  draw.rectangle(((x+6, y+3), (x+7, y+12)), fill = colorDark if strength>2 else colorLight)
  draw.rectangle(((x+9, y), (x+10, y+12)), fill = colorDark if strength>3 else colorLight)

def drawBattery(draw,xy,percent,colorDark,colorLight):
  x=xy[0]
  y=xy[1]
  draw.rectangle(((x, y), (x+22, y+12)), fill = colorDark if percent>20 else colorLight)
  draw.rectangle(((x+23, y+4), (x+23, y+8)), fill = colorDark if percent>20 else colorLight)
  draw.rectangle(((x+1, y+1), (x+21, y+11)), fill = 0)
  if(percent>10):
    draw.rectangle(((x+2, y+2), (x+4, y+10)), fill = colorDark if percent>20 else colorLight)
  if(percent>20):
    draw.rectangle(((x+6, y+2), (x+8, y+10)), fill = colorDark )
  if(percent>40):
    draw.rectangle(((x+10, y+2), (x+12, y+10)), fill = colorDark )
  if(percent>60):
    draw.rectangle(((x+14, y+2), (x+16, y+10)), fill = colorDark )
  if(percent>80):
    draw.rectangle(((x+18, y+2), (x+20, y+10)), fill = colorDark )
  
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
  return strength

measurement = namedtuple("measurement","time temp humid press lux batt")

def getBME():
  timestr=time.strftime('%I:%M%p %b %d, %Y')
  temperature,pressure,humidity = bme280.readBME280All()
  tempF =  temperature * 9 / 5 + 32
  inHg = pressure * 0.02952998751
  lux = veml7700.lux
  chan = AnalogIn(ads, ADS.P0)
  battLevel = (chan.voltage-3.1)*100.0
#  4.09 = full 3.1 = empty
# print(chan.value, chan.voltage)
  retval = measurement(timestr, str(round(tempF,1)), str(round(humidity,1)), str(round(inHg,6)), str(round(lux,1)) if lux>100 else str(lux) , round(battLevel,1))
  global data
# read in the collection
  with open("bme280data.dat", "r") as rFile:
    data=json.load(rFile)
# append the new data
    data.append(retval)
# ensure there are no more that 4400 measurements
    while(len(data)>4400):
      data.pop(0)
# write the updated collection
  with open("bme280data.dat", "w") as wFile:
    json.dump(data, wFile)
#  print( formattedStr )
# trim the memory data to 440 measurements
  endpt=len(data)
  startpt=len(data)-440
  if(startpt<0):
    startpt=0
  data=data[startpt:endpt]
  return retval

def drawPressure(draw,x,y,x2,y2):
 global data
 pressureList=[]
 smoothing=1
 count=len(data)
 # more data than pixels
 if((x2-x)<len(data)):
  smoothing=int(len(data)/(x2-x))
  count=(x2-x)
 for i in range(0,count):
   total=0
   for j in range(0,smoothing):
   	total=total+float(data[i*smoothing+j][3])
   pressureList.append(total/smoothing)
 maxP=max(pressureList)
 minP=min(pressureList)
 #print(maxP, minP)
 scaley=(y2-y)/(maxP-minP)
 scalex=len(pressureList)/(x2-x)
 #print(scalex, scaley)
 currentx=x
 for p in pressureList:
   #print(p, (p-minP)*scaley+y) 
   draw.rectangle(((currentx, y2), (scalex+currentx, y2-(p-minP)*scaley)), fill = 1)
   currentx=currentx+scalex

def drawLayout1(draw):
 strength=getWiFiStrength()
 drawWifi(draw,(212-16,0),strength,1,2)

 measure=getBME()
 text=measure.temp+"F"
 font=ImageFont.truetype(FredokaOne,64)
 draw.text((0,-15),text,1,font)
 
 drawBattery(draw, (212-44,0), measure.batt, 1,2)

 text=measure.lux
 font=ImageFont.truetype(HankenGrotesk,18)
 draw.text((145,30),text,1,font)

 drawPressure(draw, 0, 55, 110, 83)

 text=measure.humid+"%"
 font=ImageFont.truetype(FredokaOne,32)
 w, h = font.getsize(text)
 draw.text(((212-w),(104-h)-20),text,1,font)

 text=measure.time
 font=ImageFont.truetype(HankenGrotesk,18)
 w, h = font.getsize(text)
 draw.text(((212-w)/2,104-h),text,1,font)

def drawLayout2(draw):
 strength=getWiFiStrength()
 drawWifi(draw,(212-16,0),strength,1,2)
 
 measure=getBME()
 text=measure.temp+"F"
 font=ImageFont.truetype(FredokaOne,48)
 w, h = font.getsize(text)
 draw.text((0,7),text,1,font)

 text=measure.humid+"%"
 font=ImageFont.truetype(FredokaOne,30)
 w2, h2 = font.getsize(text)
 draw.text(((212-w2),(h-h2)),text,1,font)

 text=measure.time
 font=ImageFont.truetype(HankenGrotesk,18)
 w, h = font.getsize(text)
 draw.text((0,-4),text,1,font)

 
def updateGreenHouseDisplay():
 img = Image.new("P", (212, 104))
 draw = ImageDraw.Draw(img)
 drawLayout1(draw)
 
 inky_display.set_image(img)
 inky_display.show()
 img.putpalette([255,255,255,0,0,0,255,0,0])
 img.save("currentDisplay.png")

formattedText = namedtuple("formattedText","text fontname fontsize center")

if __name__ == '__main__':
  updateGreenHouseDisplay()
