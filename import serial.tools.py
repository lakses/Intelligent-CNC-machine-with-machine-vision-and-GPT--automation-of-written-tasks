import serial.tools.list_ports as port_list
import serial
import time
ports = list(port_list.comports())
for p in ports:
    print(p)
ser = serial.Serial('COM4', 9600)
file = open("out.gcode", "r")
while True:
    content = str.encode(file.readline())
    ser.write(content)
    time.sleep(1)
    if not content:
      break
file.close()
print(ser.read)  
ser.close
