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
#from datetime import datetime
import pytz

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


def convertToUTC(dtToConvert):
	miFechaTimestamps=float(TimeOfFix.datetime("%s"))
	utc_offset = datetime.fromtimestamp(miFechaTimestamps) - datetime.utcfromtimestamp(miFechaTimestamps)
	return dtToConvert + utc_offset

@app.route('/status')
def start():
    return 'Server is running...'

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind(("23.239.5.206",5000))
print " ******************************** "
print "UDP server up and listening !!!"
#print "punto break"

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#print "bufferSize: ", bufferSize
#print "UDPClientSocket: ", UDPClientSocket

# Listen for incoming datagrams
while(True):
	#print "Dentro del while"
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message1 = bytesAddressPair[0]
        #print "Message1: ", message1

        addr_port = bytesAddressPair[1]
        address = addr_port[0]
        port_addr = addr_port[1]
	#print "address: ", address
	#print "port_addr: ", port_addr

        message = binascii.hexlify(message1)
        print "Message: ", message
	#print "Len Message: ",len(message)
	if len(message) > 10:
	        clientMsg = "Message from Client:{}".format(message)
	        clientIP  = "Client IP Address:{}".format(address)
	        clientPort = "Client Port Address:{}".format(port_addr)

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

		Update_Time = (datetime.datetime.fromtimestamp(int(int(message[26:34], 16))).strftime('%d-%m-%Y %H:%M:%S'))
	        #print "Update Time:", Update_Time
	        TimeOfFix = (datetime.datetime.fromtimestamp(int(int(message[34:42], 16) - 18000)).strftime('%Y-%m-%d %H:%M:%S'))
	        print "TimeOfFix:", TimeOfFix

		#Offset_time = TimeOfFix - datetime.timedelta(hours=5)
		#print "Offset time: ", Offset_time

        	Lat = message[42:50]
	        if  int(Lat[0:1],16) > 7:
        	    Latitude = round((-0.0000001*(bit_not(int(Lat,16))+1)),7)
	        else:
        	    Latitude = round((0.0000001*(bit_not(int(Lat,16)))),7)

	        Long = message[50:58]
	        if  int(Long[0:1],16) > 7:
        	    Longitude = round((-0.0000001*(bit_not(int(Long,16))+1)),7)
	        else:
	            Longitude = round((0.0000001*(bit_not(int(Long,16)))),7)

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
		User_Msg_xbee = message[106:len(message)]
		print "User_Msg_bee: ", User_Msg_xbee

		try:
	        	#User_Msg = binascii.unhexlify(message[106:((2*(int(message[102:106],16)))+106-2)])
			User_Msg = binascii.unhexlify(User_Msg_xbee[User_Msg_xbee.find("3e"):len(User_Msg_xbee)])
			print "User_Msg: ", User_Msg

		except TypeError:
			print "Error User_Msg"
			User_Msg = 'EE'
			print "User_Msg: ", User_Msg
			print "len(User_Msg) :", len(User_Msg)

	        AckMessage = OptionsByte + MobileIDLength + MobileID + MobileIDLen + MobileIDType + Service_Type + Message_Type + Sequence + Type_ + ACK_ + Spare_ + AppVersion_

		#User_Msg discrimina data real
		if len(User_Msg) > 2:

			#inic = User_Msg.find(">")
			#inic = 1
			data = User_Msg[1:(len(User_Msg) - 1)]
			print "data: ", data

		        items = data.split(";")
		        mac = items[0]
		        mac = mac[0:len(mac)]
			print "mac ", mac
			if len(mac) < 23:
				mac = 'EE:EE:EE:EE:EE:EE:EE:EE'

			try:
			        humidity = items[1]
		        except IndexError:
				print "Error humidity"
				humidity = 0
			try:
				humidity2 = items[2]
		        except IndexError:
				print "Error humidity2"
				humidity2 = 0
			try:
				temperature = items[3]
			except IndexError:
				print "Error temperatura"
				temperature = 0
			try:
			        temperature2 = items[4]
			except IndexError:
				print "Error temperature"
				temperature2 = 0
			try:
			        ammonia = items[5]
			except IndexError:
				print "Error ammonia"
				ammonia = 0
			try:
			        ammonia2 = items[6]
			except IndexError:
				print "Error ammonia2"
				ammonia2 = 0
			try:
			        speed = items[7]
			except IndexError:
				print "Error speed"
				speed = 0
			try:
			        co2 = items[8]
			except IndexError:
				print "Error co2"
				co2 = 0
			try:
			        battery = items[9]
			except IndexError:
				print "Error battery"
				battery = 0

		        # creating sql insert sentence
		        insertSQL = "insert into data"
		        insertFields = "created, latitude, longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery"
       			insertValuePH = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
		        sqlValues = [TimeOfFix, Latitude, Longitude, mac, humidity, humidity2, temperature, temperature2, ammonia, ammonia2, speed, co2, battery]
       			insertSQL = insertSQL + "(" + insertFields + ") values (" + insertValuePH + ")"
			#print "sqlValues: ", sqlValues

			connection = mysql.connect()
			cursor = connection.cursor()
			cursor.execute(insertSQL,tuple(sqlValues))
			connection.commit()
			print "Message insert to MySQL"

		msgFromClient = AckMessage
		#print "AckMessage: ", AckMessage

		bytesToSend = binascii.unhexlify(msgFromClient)
		#print "bytesToSend: ", bytesToSend

	        serverAddressPort = (address, port_addr)
		#print "serverAddressPort: ", serverAddressPort

	        # Send to server using created UDP socket
       		size = UDPServerSocket.sendto(bytesToSend, serverAddressPort)
		#print "UDPClienteSocket: ", size


	else:
		print "Error message menor a 10 caracteres"

	print "Fin"

def setupLogger():
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    global logger


if __name__ == "__main__":
    setupLogger()
    app.run(host= '0.0.0.0', port=5000)
