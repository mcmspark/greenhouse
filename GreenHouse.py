import subprocess
import json
import GreenHouseReadSensors
import GreenHouseDisplay
import time
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# bad idea
#def systemShutdown():
#  subprocess.call("sudo shutdown -h now", shell=True)

currentWifiState=False

def turnOnTheWifi(state):
  global currentWifiState
  if state!=currentWifiState :
    cmd=["ifconfig","wlan0", "up" if state else "down"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    currentWifiState=state

def turnOffTheActLight(state):
  if state:
    trigger='none\n'
    brightness='1\n'
  else:
    trigger='cpu0\n'
    brightness='0\n'
  try:
    with open("/sys/class/leds/led0/trigger","w") as f:
      f.write(trigger)
    with open("/sys/class/leds/led0/brightness","w") as f:
      f.write(brightness)
  except:
    print("you must run as root to disable the act light")


def wifiPowerSchedule():
  # disable wifi at night and for the bottom part of the hour
  tmval = time.localtime()
  enableWifi=(tmval.tm_hour>5 and tmval.tm_hour<23) and (tmval.tm_min>49 or tmval.tm_min<11)
  turnOnTheWifi(enableWifi)

def powerSaver(seconds,measurements):
  if measurements.batt<10.0:
    # no power
    turnOnTheWifi(False)
    return 1800
  if float(measurements.lux)>10.0:
    # sun is up
    turnOnTheWifi(True)
    return 300
  if seconds<900 and float(measurements.lux)<10.0:
    # set seconds to 900 and wait 15 minutes
    return 900
  if seconds>800 and float(measurements.lux)<10.0:
    # it is dark, go into low power mode and only update every 20 miutes
    turnOnTheWifi(False)
    return 1200
  return 300

def recordHistory(measurements):
  data = []
  try:
    # read in the collection
    with open("GreenHouseData.json", "r") as rFile:
      data=json.load(rFile)
  except:
    print("Creating GreenHouse.json file")
  # append the new data
  data.append(measurements._asdict())
  # ensure there are no more than 4400 measurements
  while(len(data)>4400):
    data.pop(0)
  # write the updated collection
  with open("GreenHouseData.json", "w") as wFile:
    json.dump(data, wFile)
  # trim the memory data to 440 recent measurements
  endpt=len(data)
  startpt=len(data)-440
  if(startpt<0):
    startpt=0
  return data[startpt:endpt]

webServer = None #seting the global variable
serverThread = None

class WebServer(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global webServer
    webServer = ThreadingHTTPServer(('', 8080), MyServer)
    self.running = True #setting the thread running to true
 
  def run(self):
    global webServer
    while(self.running):
      webServer.timeout=60
      webServer.handle_request()
    webServer.server_close()
    print("Server Shutdown")

#measurement = namedtuple("measurement","time temp humid press lux batt wifi")
class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
      try:
        if self.path == '/':
            self.path = 'index.html'
        if self.path == '/measure':
          measurements=GreenHouseReadSensors.getMeasurements()
          self.send_response(200)
          self.send_header("Content-type", "application/json")
          self.end_headers()
          self.wfile.write(bytes(json.dumps(measurements._asdict()),'utf-8'))
          return
        return SimpleHTTPRequestHandler.do_GET(self)
      except IOError:
        self.send_error(404,'File Not Found: %s' % self.path)

def mainLoop(seconds):
  global serverThread
  try:
    serverThread = WebServer() # create the thread
    serverThread.start() # start it up
    while True:
      measurements=GreenHouseReadSensors.getMeasurements()
      seconds=powerSaver(seconds, measurements)
      data = recordHistory(measurements)
      GreenHouseDisplay.updateGreenHouseDisplay(measurements, data)
      time.sleep(int(seconds))
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("closing")
    serverThread.running=False
  turnOnTheWifi(True)

if __name__ == '__main__':
  turnOffTheActLight(True)
  mainLoop(300)
  turnOffTheActLight(False)

