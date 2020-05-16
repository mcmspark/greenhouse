import subprocess
import json
import GreenHouseReadSensors
import GreenHouseDisplay
import time
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

def turnOffTheActLight(state):
  if state :
    cmd = ["./lightoff.sh"]
  else :
    cmd = ["./lighton.sh"]
  subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def recordHistory(measurements):
  data = []
  # read in the collection
  with open("GreenHouseData.json", "r") as rFile:
    data=json.load(rFile)
    # append the new data
    data.append(measurements)
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
      webServer.timeout=10
      webServer.handle_request()
    webServer.server_close()
    print("Server Shutdown")

class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
      try:
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)
        #f = open('currentDisplay.png','rb')
        #self.send_response(200)
        #self.send_header("Content-type", "image/png")
        #self.end_headers()
        #self.wfile.write(f.read())
        #f.close()
        #return
      except IOError:
        self.send_error(404,'File Not Found: %s' % self.path)

def mainLoop(seconds):
  global serverThread
  try:
    serverThread = WebServer() # create the thread
    serverThread.start() # start it up
    while True:
      measurements=GreenHouseReadSensors.getMeasurements()
      data = recordHistory(measurements)
      GreenHouseDisplay.updateGreenHouseDisplay(measurements, data)
      time.sleep(int(seconds))
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("closing")
    serverThread.running=False

if __name__ == '__main__':
  mainLoop(300)
