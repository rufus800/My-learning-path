import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialinst = serial.Serial()

portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))
val = input("select Port: COM")

for x in range(0,len(portList)):
    if portList[x].startswith("COM"+ str(val)):
        portVar= "COM" +str(val)
        print(portList[x])

serialinst.buadrate = 9600
serialinst.port = portVar
serialinst.open()

while True:
    if serialinst.in_waiting:
        packet = serialinst.readline()
        print(packet.decode('utf'))
        break

serialinst.close()

    
    