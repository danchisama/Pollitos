import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Note: IP/Port might need update
HOST = '23.239.5.206'
PORT = 5805

print "Connecting to %s:%d" % (HOST, PORT)
s.connect((HOST, PORT))
s.sendall('Hello, world')

data = s.recv(1024)
s.close() # Fixed typo: cloe -> close
print 'Received', repr(data)
