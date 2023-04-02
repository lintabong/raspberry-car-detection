import sys
import os
import binascii
from time import sleep, time
from datetime import datetime
import cv2
import pyrebase
import serial
from dotenv import load_dotenv

load_dotenv()


def generate() -> str:
    timestamp = "{:x}".format(int(time()))
    rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
    return timestamp + rest

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f"%(position)
    return position


cascade_src = "cars.xml"

gpgga_info = "$GPGGA,"
GPGGA_buffer = 0
NMEA_buff = 0

# ser = serial.Serial ("/dev/ttyS0")
# gpgga_info = "$GPGGA,"
# GPGGA_buffer = 0
# NMEA_buff = 0

# received_data = (str)(ser.readline()) #read NMEA string received
# GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                
# if (GPGGA_data_available>0):
#     GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after “$GPGGA,” string
#     NMEA_buff = (GPGGA_buffer.split(','))
#     nmea_time = []
#     nmea_latitude = []
#     nmea_longitude = []
#     nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
#     nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
#     nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
#     print("NMEA Time: ", nmea_time,"\n")
#     lat = (float)(nmea_latitude)
#     lat = convert_to_degrees(lat)
#     longi = (float)(nmea_longitude)
#     longi = convert_to_degrees(longi)
#     print("NMEA Latitude:", lat,"NMEA Longitude:", longi,"\n")  

# config firebase
firebaseConfig = {
  "apiKey": os.getenv("FIREBASE_APIKEY"),
  "authDomain": os.getenv("FIREBASE_AUTHDOMAIN"),
  "databaseURL": os.getenv("FIREBASE_DATABASEURL"),
  "projectId": os.getenv("FIREBASE_PROJECTID"),
  "storageBucket": os.getenv("FIREBASE_STORAGEBUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGINGSENDERID"),
  "appId": os.getenv("FIREBASE_APPID")
}

firebase    = pyrebase.initialize_app(firebaseConfig)
storage     = firebase.storage()
db          = firebase.database()

r = 1

car_cascade = cv2.CascadeClassifier(cascade_src)
img = cv2.imread("sample/cars0.jpeg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
cars = car_cascade.detectMultiScale(gray, 1.1, 1)

now = datetime.now()

data = {
    "id": generate(),
    "detection": len(cars),
    "distance": [],
    "at": str(now),
    "speed": ""
}

print("detection: ", len(cars))
print("distance: ")
for i, (x, y, w, h) in enumerate(cars):
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    print("   {}   {:.5f}".format((i+1), img.shape[0]/w))

    data["distance"].append("{:.5f}".format(img.shape[0]/w))

db.child(f"data/{now.year}/{now.month}/{now.day}/{int(datetime.timestamp(datetime.now()))}/").set(data)

cv2.imshow('video', img)
cv2.waitKey(0)
cv2.destroyAllWindows()