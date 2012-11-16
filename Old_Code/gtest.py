import serial
 
 
# open the serial port for the balance
tempHumidity = serial.Serial(port='COM8', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2.0, xonxoff=True, rtscts=True)
tempHumidity.write("\n\n\n\n\n\n\n")
tempHumidity.write("x")
a=0
while a<10:
 
   bline = tempHumidity.readline()
   
   print bline, "--", len(bline)
   #balance.write("WS 0\r\n")
   #balance.write("W1W0\r\n")
   
   a += 1
