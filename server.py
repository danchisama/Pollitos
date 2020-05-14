import socket

# Create a TCP/IP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
s.bind(('23.239.5.206', 5000))

s.listen(1)
conn, addr = s.accept()

while 1:
	data = conn.recv(1024)
	if not data:
		break
	conn.sendall(data)
conn.close()
