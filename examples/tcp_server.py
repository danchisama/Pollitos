import socket

# Create a TCP/IP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
# Note: IP might need update depending on environment
HOST = '23.239.5.206'
PORT = 5000

print "TCP Echo Server starting on %s:%d" % (HOST, PORT)
s.bind((HOST, PORT))

s.listen(1)
conn, addr = s.accept()
print "Connected by", addr

while True:
      data = conn.recv(1024)
      if not data:
                break
            conn.sendall(data)

conn.close()
