import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('23.239.5.206', 5805))
s.sendall('Hello, world')
data = s.recv(1024)
s.cloe()
print 'Received', repr(data)
