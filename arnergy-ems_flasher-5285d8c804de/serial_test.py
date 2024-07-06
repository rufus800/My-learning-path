import serial 
import serial.tools.list_ports 

BAUD_RATE = 115200
ports = next(serial.tools.list_ports.grep("0483:5740"))
print(f"Found port on {ports[0]}.")
ser = serial.serial_for_url(ports[0], BAUD_RATE, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,0)
ser.timeout = 10  #10 seconds timeout 

print(ser.portstr)
result = str(ser.read(100))
print(result.find("NoResp"))
