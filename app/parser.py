import binascii
import datetime

# Constant LMU ACK configuration
SERVICE_TYPE = '02'
MESSAGE_TYPE = '01'
TYPE_ = '02'
ACK_ = '00'
SPARE_ = '00'
APP_VERSION = '0000'

def bit_not(n):
      """Perform bitwise NOT operation."""
      return (1 << n.bit_length()) - 1 - n

def parse_lmu_message(hex_message):
      """
          Parses a hexadecimal LMU protocol message.
              Returns a dictionary with extracted fields or None if invalid.
                  """
      if len(hex_message) <= 10:
                return None

      try:
                data = {}
                data['options_byte'] = hex_message[0:2]
                data['mobile_id_length'] = hex_message[2:4]
                data['mobile_id'] = hex_message[4:14]
                data['mobile_id_len_field'] = hex_message[14:16]
                data['mobile_id_type'] = hex_message[16:18]
                data['sequence'] = hex_message[22:26]

          # Time parsing
                data['update_time'] = datetime.datetime.fromtimestamp(int(hex_message[26:34], 16)).strftime('%Y-%m-%d %H:%M:%S')
                # fix_time with -5h offset (18000 seconds) as seen in original code
                data['fix_time'] = datetime.datetime.fromtimestamp(int(hex_message[34:42], 16) - 18000).strftime('%Y-%m-%d %H:%M:%S')

          # Latitude parsing
                lat_hex = hex_message[42:50]
                if int(lat_hex[0:1], 16) > 7:
                              data['latitude'] = round((-0.0000001 * (bit_not(int(lat_hex, 16)) + 1)), 7)
      else:
                    data['latitude'] = round((0.0000001 * (int(lat_hex, 16))), 7)

          # Longitude parsing
                long_hex = hex_message[50:58]
        if int(long_hex[0:1], 16) > 7:
                      data['longitude'] = round((-0.0000001 * (bit_not(int(long_hex, 16)) + 1)), 7)
else:
            data['longitude'] = round((0.0000001 * (int(long_hex, 16))), 7)

        # User Message parsing (XBee/Sensors)
          user_msg_hex = hex_message[106:]
        start_index = user_msg_hex.find("3e") # find '>'
        if start_index != -1:
                      user_msg_raw = binascii.unhexlify(user_msg_hex[start_index:])
                      # Clean data: remove '>' and '<' if present
                      clean_data = user_msg_raw.strip(">").strip("<")
                      items = clean_data.split(";")

            data['mac'] = items[0] if len(items) > 0 else 'EE:EE:EE:EE:EE:EE:EE:EE'
            data['humidity'] = items[1] if len(items) > 1 else 0
            data['humidity2'] = items[2] if len(items) > 2 else 0
            data['temperature'] = items[3] if len(items) > 3 else 0
            data['temperature2'] = items[4] if len(items) > 4 else 0
            data['ammonia'] = items[5] if len(items) > 5 else 0
            data['ammonia2'] = items[6] if len(items) > 6 else 0
            data['speed'] = items[7] if len(items) > 7 else 0
            data['co2'] = items[8] if len(items) > 8 else 0
            data['battery'] = items[9] if len(items) > 9 else 0
else:
            data['mac'] = 'EE:EE:EE:EE:EE:EE:EE:EE'
              for field in ['humidity', 'humidity2', 'temperature', 'temperature2', 'ammonia', 'ammonia2', 'speed', 'co2', 'battery']:
                                data[field] = 0

        return data
except Exception as e:
        print "Error parsing message: ", e
        return None

def create_ack(parsed_data):
      """Creates an ACK message based on parsed data fields."""
    return (parsed_data['options_byte'] + 
                        parsed_data['mobile_id_length'] + 
                        parsed_data['mobile_id'] + 
                        parsed_data['mobile_id_len_field'] + 
                        parsed_data['mobile_id_type'] + 
                        SERVICE_TYPE + 
                        MESSAGE_TYPE + 
                        parsed_data['sequence'] + 
                        TYPE_ + 
                        ACK_ + 
                        SPARE_ + 
                        APP_VERSION)
