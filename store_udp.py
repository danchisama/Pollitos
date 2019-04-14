import os
import sys
import logging
import time
import traceback
import datetime
import binascii
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask import request
from flaskext.mysql import MySQL
import socket

# Constant LMU ACK
Service_Type = '02'
Message_Type = '01'
Type_ = '01'
ACK_ = '00'
Spare_ = '00'
AppVersion_ = '000000'


clienteIP = '23.239.5.206'
clientPort = '5000'
bufferSize = 2048

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

log_directory = './logs'
log_file = log_directory + "/store_app.log"

def bit_not(n):
    return (1 << n.bit_length()) - 1 - n

@app.route('/status')
def start():
    return 'Server is running...'

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind(("23.239.5.206",5000))
print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    #print "bytesAddressPair", bytesAddressPair

    message1 = bytesAddressPair[0]
    addr_port = bytesAddressPair[1]
    address = addr_port[0]
    port_addr = addr_port[1]

    message = binascii.hexlify(message1)

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    clientPort = "Client Port Address:{}".format(port_addr)

    OptionsByte = message[0:2]
    #print "OptionsByte:", OptionsByte 

    MobileIDLength = message[2:4]
    #print "MobileIDLength:", MobileIDLength

    MobileID = message[4:14]
    #print "MobileID:", MobileID

    MobileIDLen = message[14:16]
    #print "MobileIDLen:", MobileIDLen

    MobileIDType = message[16:18]
    #print "MobileIDType:", MobileIDType

    #Service_Type = message[18:20]
    #print "Service Type:", Service_Type

    #Message_Type = message[20:22]
    #print "Message Type:", Message_Type

    Sequence = message[22:26]
    #print "Sequence#:", Sequence

    Update_Time = (datetime.datetime.fromtimestamp(int(int(message[26:34], 16))).strftime('%d-%m-%Y %H:%M:%S'))
    print "Update Time:", Update_Time

    TimeOfFix = (datetime.datetime.fromtimestamp(int(int(message[34:42], 16))).strftime('%d-%m-%Y %H:%M:%S'))
    print "TimeOfFix:", TimeOfFix

    Lat = message[42:50]
    if  int(Lat[0:1],16) > 7:
        Latitude = round((-0.0000001*(bit_not(int(Lat,16))+1)),7)
        print "Latitude:", Latitude
    else:
        Latitude = round((0.0000001*(bit_not(int(Lat,16)))),7)
        print "Latitude:", Latitude

    Long = message[50:58]
    if  int(Long[0:1],16) > 7:
        Longitude = round((-0.0000001*(bit_not(int(Long,16))+1)),7)
        print "Longitude:", Longitude
    else:
        Longitude = round((0.0000001*(bit_not(int(Long,16)))),7)
        print "Longitude:", Longitude

    #Altitude = message[58:66]
    #print "Altitude:", Altitude

    #Speed = message[66:74]
    #print "Speed:", Speed

    #Heading = message[74:78]
    #print "Heading:", Heading

    #Satellites = message[78:80]
    #print "Satellites:", Satellites

    #FixStatus = message[80:82]
    #print "FixStatus:", FixStatus

    #Carrier = message[82:86]
    #print "Carrier:", Carrier

    #RSSI = message[86:90]
    #print "RSSI:", RSSI

    #CommState = message[90:92]
    #print "CommState:", CommState

    #HDOP = message[92:94]
    #print "HDOP:", HDOP

    #Inputs = message[94:96]
    #print "Inputs:", Inputs

    #UnitStatus = message[96:98]
    #print "UnitStatus:", UnitStatus

    #User_Msg_Route = message[98:100]
    #print "User Msg Route:", User_Msg_Route

    #User_Msg_Id = message[100:102]
    #print "User Msg Id:", User_Msg_Id

    #User_Msg_Length = message[102:106]
    #print "User Msg Length:", User_Msg_Length

    User_Msg = binascii.unhexlify(message[106:((2*(int(message[102:106],16)))+106-2)])
    print "User Msg:", User_Msg

    AckMessage = OptionsByte + MobileIDLength + MobileID + MobileIDLen + MobileIDType + Service_Type + Message_Type + Sequence + Type_ + ACK_ + Spare_ + AppVersion_

    data = User_Msg[1:(len(User_Msg) - 1)]

    items = data.split(";")

    # this map stores the information that will be inserted into a data table
    myList = []
    mac = items[0]
    #mac = mac[0:len(mac)-2]
    print "MAC: ", mac

    humidity = items[1]
    print "Humidity: ", humidity

    humidity2 = items[2]
    print "Humidity2: ", humidity2

    temperature = items[3]
    print "Temperature: ", temperature

    temperature2 = items[4]
    print "Temperature2: ", temperature2

    ammonia = items[5]
    print "Ammonia: ", ammonia

    ammonia2 = items[6]
    print "Ammonia2: ", ammonia2

    speed = items[7]
    print "Speed: ", speed

    co2 = items[8]
    print "CO2: ", co2

    battery = items[9]
    print "Battery: ", battery

    # creating sql insert sentence
    insertSQL = "insert into data"
    insertFields = "created, ,latitude, longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery"
    insertValuePH = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
    sqlValues = [TimeOfFix, Latitude, Longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery]
    insertSQL = insertSQL + "(" + insertFields + ") values (" + insertValuePH + ")"
    
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(insertSQL,tuple(sqlValues))
    connection.commit()

    msgFromClient = AckMessage
    bytesToSend = str.encode(msgFromClient)
    serverAddressPort = (clienteIP, 5000)

    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)


def setupLogger():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    global logger


if __name__ == "__main__":
    setupLogger()
    app.run(host= '0.0.0.0', port=5000)
