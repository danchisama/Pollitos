import socket
UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

listen_addr = ("",5000)
UDPSock.bind(listen_addr)

while True:
	print "while True ..."
	data,addr = UDPSock.recvfrom(1024)
	print data.strip(),addr
