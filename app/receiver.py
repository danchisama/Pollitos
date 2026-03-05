import socket
import binascii
import os
from flask import Flask
from parser import parse_lmu_message, create_ack
from database import DatabaseManager

app = Flask(__name__)

# Configuration (Ideally these should be in a config file or .env)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'dataP4ssw0rd@2016*-'
app.config['MYSQL_DATABASE_DB'] = 'data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db = DatabaseManager(app)

SERVER_IP = "0.0.0.0"
UDP_PORT = 5000
BUFFER_SIZE = 2048

@app.route('/status')
def status():
      return 'UDP Receiver Server is running...'

def run_receiver():
      # Create and bind UDP server socket
      server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
      server_socket.bind((SERVER_IP, UDP_PORT))

    print "********************************"
    print "UDP Receiver listening on %s:%d" % (SERVER_IP, UDP_PORT)
    print "********************************"

    while True:
              try:
                            bytes_pair = server_socket.recvfrom(BUFFER_SIZE)
                            raw_message = bytes_pair[0]
                            client_address = bytes_pair[1]

                  hex_message = binascii.hexlify(raw_message)
            print "Received: ", hex_message

            parsed_data = parse_lmu_message(hex_message)

            if parsed_data:
                              # Save to DB
                              if db.insert_sensor_data(parsed_data):
                                                    print "Data stored in MySQL"

                              # Send ACK
                              ack_hex = create_ack(parsed_data)
                              ack_bytes = binascii.unhexlify(ack_hex)
                              server_socket.sendto(ack_bytes, client_address)
                              print "ACK sent to %s" % (str(client_address))
else:
                print "Message too short or invalid LMU format"

except Exception as e:
            print "Receiver error: ", e

if __name__ == "__main__":
      # Start the Flask app for /status in a separate thread if needed, 
      # but for simplicity, we'll just run the UDP loop.
      # To run both, you would need threading or a different architecture.
      run_receiver()
