from flaskext.mysql import MySQL

class DatabaseManager:
      def __init__(self, app):
                self.mysql = MySQL()
                self.mysql.init_app(app)

      def insert_sensor_data(self, data):
                """Inserts parsed sensor data into the 'data' table."""
                try:
                              insert_sql = """
                                              INSERT INTO data (
                                                                  created, latitude, longitude, mac, humidity, humidity2, 
                                                                                      temperature, temperature2, ammonia, ammonia2, speed, co2, battery
                                                                                                      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                                                                                                  """
                              values = (
                                  data['fix_time'], data['latitude'], data['longitude'], data['mac'],
                                  data['humidity'], data['humidity2'], data['temperature'], data['temperature2'],
                                  data['ammonia'], data['ammonia2'], data['speed'], data['co2'], data['battery']
                              )

                    connection = self.mysql.connect()
                    cursor = connection.cursor()
                    cursor.execute(insert_sql, values)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return True
except Exception as e:
            print "Database error: ", e
            return False
