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
Type_ = '02'
ACK_ = '00'
Spare_ = '00'
AppVersion_ = '0000'


clienteIP = '23.239.5.206'
clientPort = '5000'
bufferSize = 2048

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'dataP4ssw0rd@2016*-'
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

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Listen for incoming datagrams
while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message1 = bytesAddressPair[0]
        #print "Message1: ", message1

        addr_port = bytesAddressPair[1]
        address = addr_port[0]
        port_addr = addr_port[1]

        message = binascii.hexlify(message1)
        #print "Message: ", message

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        clientPort = "Client Port Address:{}".format(port_addr)
    except:
        print "Error en byteAddressPair"
    
    try:  
        OptionsByte = message[0:2]
        MobileIDLength = message[2:4]
        MobileID = message[4:14]
        MobileIDLen = message[14:16]
        MobileIDType = message[16:18]
        #Service_Type = message[18:20]
        #print "Service Type:", Service_Type
        #Message_Type = message[20:22]
        #print "Message Type:", Message_Type
        Sequence = message[22:26]
        #print "Sequence#:", Sequence
    except:
        print "Error en message[xx:xx]"
       
    try:
        Update_Time = (datetime.datetime.fromtimestamp(int(int(message[26:34], 16))).strftime('%d-%m-%Y %H:%M:%S'))
        #print "Update Time:", Update_Time
        TimeOfFix = (datetime.datetime.fromtimestamp(int(int(message[34:42], 16))).strftime('%Y-%m-%d %H:%M:%S'))
        print "TimeOfFix:", TimeOfFix
    except:
        print "Error tiempo"
    
    try:
        Lat = message[42:50]
        if  int(Lat[0:1],16) > 7:
            Latitude = round((-0.0000001*(bit_not(int(Lat,16))+1)),7)
        else:
            Latitude = round((0.0000001*(bit_not(int(Lat,16)))),7)
   exception:
        print "Error Lat"
   

    try:
        Long = message[50:58]
        if  int(Long[0:1],16) > 7:
            Longitude = round((-0.0000001*(bit_not(int(Long,16))+1)),7)
        else:
            Longitude = round((0.0000001*(bit_not(int(Long,16)))),7)
    exception:
        print "Error Long"
        
        #Altitude = message[58:66]
        #Speed = message[66:74]
        #Heading = message[74:78]
        #Satellites = message[78:80]
        #FixStatus = message[80:82]
        #Carrier = message[82:86]
        #RSSI = message[86:90]
        #CommState = message[90:92]
        #HDOP = message[92:94]
        #Inputs = message[94:96]
        #UnitStatus = message[96:98]
        #User_Msg_Route = message[98:100]
        #User_Msg_Id = message[100:102]
        #User_Msg_Length = message[102:106]
    
    try:
        User_Msg = binascii.unhexlify(message[106:((2*(int(message[102:106],16)))+106-2)])
    exception:
        print "Error User_Msg"
        
    try:
        AckMessage = OptionsByte + MobileIDLength + MobileID + MobileIDLen + MobileIDType + Service_Type + Message_Type + Sequence + Type_ + ACK_ + Spare_ + AppVersion_
        data = User_Msg[1:(len(User_Msg) - 1)]
    exception:
        print "data"
    
    try:
        items = data.split(";")
        mac = items[0]
        mac = mac[1:len(mac)]
    exception:
        print "Error MAC"
        
    try:
        humidity = items[1]
        humidity2 = items[2]
        temperature = items[3]
        temperature2 = items[4]
        ammonia = items[5]
        ammonia2 = items[6]
        speed = items[7]
        co2 = items[8]
        battery = items[9]
    exception:
        print "Error en item[x]"
        
    try:
        # creating sql insert sentence
        insertSQL = "insert into data"
        insertFields = "created, latitude, longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery"
        insertValuePH = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        sqlValues = [TimeOfFix, Latitude, Longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery]
        insertSQL = insertSQL + "(" + insertFields + ") values (" + insertValuePH + ")"
    exception:
        print "Error create data to insert BD"
        
    try:    
        bytesToSend = binascii.unhexlify(AckMessage)
        serverAddressPort = (address, port_addr)

        # Send to server using created UDP socket
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    exception:
        print "Error send Ack"
        
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(insertSQL,tuple(sqlValues))
        connection.commit()
    exception:
        print "Error insert data DB"
        

def setupLogger():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    global logger


if __name__ == "__main__":
    setupLogger()
    app.run(host= '0.0.0.0', port=5000)
