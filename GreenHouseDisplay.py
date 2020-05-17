import time
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from font_hanken_grotesk import HankenGrotesk
from collections import namedtuple

measurement = namedtuple("measurement","time temp humid press lux batt wifi")

inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.WHITE)

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
  draw.rectangle(((x, y), (x+22, y+12)), fill = colorDark if percent>30 else colorLight)
  draw.rectangle(((x+23, y+4), (x+23, y+8)), fill = colorDark if percent>30 else colorLight)
  draw.rectangle(((x+1, y+1), (x+21, y+11)), fill = 0)
  if(percent>20):
    draw.rectangle(((x+2, y+2), (x+4, y+10)), fill = colorDark if percent>30 else colorLight)
  if(percent>40):
    draw.rectangle(((x+6, y+2), (x+8, y+10)), fill = colorDark )
  if(percent>50):
    draw.rectangle(((x+10, y+2), (x+12, y+10)), fill = colorDark )
  if(percent>70):
    draw.rectangle(((x+14, y+2), (x+16, y+10)), fill = colorDark )
  if(percent>90):
    draw.rectangle(((x+18, y+2), (x+20, y+10)), fill = colorDark )

def drawPressure(draw,x,y,x2,y2,data):
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
   	total=total+float(data[i*smoothing+j]["press"])
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

def drawLayout(draw, measurements, data ):
 
 drawWifi(draw,(212-16,0),measurements.wifi,1,2)

 text=measurements.temp+"F"
 font=ImageFont.truetype(FredokaOne,64)
 draw.text((0,-15),text,1,font)
 
 drawBattery(draw, (212-44,0), measurements.batt, 1,2)

 text=measurements.lux
 font=ImageFont.truetype(HankenGrotesk,18)
 draw.text((145,30),text,1,font)

 drawPressure(draw, 0, 55, 110, 83, data)

 text=measurements.humid+"%"
 font=ImageFont.truetype(FredokaOne,32)
 w, h = font.getsize(text)
 draw.text(((212-w),(104-h)-20),text,1,font)

 text=measurements.time
 font=ImageFont.truetype(HankenGrotesk,18)
 w, h = font.getsize(text)
 draw.text(((212-w)/2,104-h),text,1,font)
 
def updateGreenHouseDisplay(measurements, data):
 img = Image.new("P", (212, 104))
 draw = ImageDraw.Draw(img)
 drawLayout(draw, measurements, data)
 
 inky_display.set_image(img)
 inky_display.show()
 img.putpalette([255,255,255,0,0,0,255,0,0])
 img.save("currentDisplay.png")

if __name__ == '__main__':
  updateGreenHouseDisplay(measurement(time.strftime('%I:%M%p %b %d, %Y'),"75.9","45.6","19","2532",19,3),[(0,0,0,0),(0,0,0,1),(0,0,0,2),(0,0,0,3)])
