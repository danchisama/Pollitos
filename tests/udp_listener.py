import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5000
BUFFER_SIZE = 1024

print "Quick UDP Listener on port %d... (Ctrl+C to stop)" % UDP_PORT
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
      data, addr = sock.recvfrom(BUFFER_SIZE)
      print "Received message from %s: %s" % (addr, data.encode('hex'))
  
