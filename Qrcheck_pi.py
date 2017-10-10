print("Loading...")
import zbar
import cv2
import pymysql
from PIL import Image
from string import punctuation
import re
import RPi.GPIO as GPIO
import time
import picamera
from picamera.array import PiRGBArray
from picamera import PiCamera
#Setup pins for output
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(4,GPIO.OUT)
tb=GPIO.PWM(4,50)
tb.start(12.5)
print("Resetting")
time.sleep(1)
tb.stop()
#
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
print("Warming up the Camera")
time.sleep(0.3)
print("Connecting...")	
db=pymysql.connect(host="sql9.freemysqlhosting.net", user="sql9197760", passwd="hwIDaFzRZA", db="sql9197760")
ex=db.cursor(pymysql.cursors.DictCursor)
print("Connected to Database")
chars = re.escape(punctuation)
isLocked=False
try:
    scanner = zbar.Scanner()
except:
    scanner = zbar.ImageScanner()
def Granted(yit,state):
    if state:
        tb.start(1.5)
        time.sleep(1)
        tb.stop()
        for i in range(yit):
            time.sleep(.3)
            GPIO.output(27,GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(27,GPIO.LOW)
        isLocked=state
        #Relocks for Demo purpose
        tb.start(12.5)
        time.sleep(1)
        tb.stop()
    else:
        for i in range(yit):
            time.sleep(.3)
            GPIO.output(27,GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(27,GPIO.LOW)
def Denied(yit):
    print("Access Denied")
    for i in range(yit):
        time.sleep(.3)
        GPIO.output(17,GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(17,GPIO.LOW)
    print("Access Denied")
Granted(12,isLocked)
isLocked=True
print("Processing started")
try:
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        #(_,image) = cam.read() 
        image = frame.array
        nimage = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        nimage = Image.fromarray(nimage)
        
        results = scanner.scan(nimage)
        for result in results:
            if len(results) != 0:
                if ex.execute("SELECT name FROM allow_ids WHERE passkey = '{0}';".format(re.sub(r'['+chars+']', '',str(result.data.decode("utf-8"))))):
                    name=ex.fetchall()[0]['name']
                    print("Welcome, {0}".format(name))
                    Granted(6,isLocked)
                else:
                    Denied(6)
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Closing...")
    camera.close()