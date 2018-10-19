from PIL import Image
#from matplotlib import pyplot
import numpy as np
import serial
import time
from binascii import hexlify, unhexlify
serialPort = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=.5)
def sync_camera():
	sync_bit = "00"
	delay = 5
	sync_string = ""
	for i in range(0, 60):
		print("Sending sync, try " + str(i))
		serialPort.write(bytearray(unhexlify('aa0d00000000')))
		string = ""
		time.sleep(delay/1000)
		string = hexlify(serialPort.read(6))
		print("Recieved from cam: " + string)
		if "aa0e0d" in string.lower():
			print("sync recieved! String: " + string)
			sync_string = string
			continue
		if "aa0d00000000" in string and sync_string != "":
			print("Sync ACK: " + string)
			sync_bit = sync_string[6:8]
			print("sending sync ack with bit " + sync_bit + "...")

			serialPort.write(bytearray(unhexlify("AA0E00"+sync_bit+"0000")))
			print("synced!")
			break
		else:
			sync_string = ""
		delay += 1
	return sync_bit
#serialPort.write(bytearray(unhexlify("AA08000000FF")))
sync = sync_camera()
time.sleep(2)

serialPort.write(bytearray(unhexlify("AA0100030307")))
print("sent: AA0100030307")
time.sleep(50/1000)
print(hexlify(serialPort.read(6)))
serialPort.write(bytearray(unhexlify("AA0501000000")))
print("sent: AA0501000000")
time.sleep(50/1000)
print(hexlify(serialPort.read(6)))
serialPort.write(bytearray(unhexlify("AA1500000000")))
print("Sent: AA1500000000")
time.sleep(50/1000)
print(hexlify(serialPort.read(6)))
# get picture
serialPort.write(bytearray(unhexlify("AA0402000000")))
print("sent: AA0402000000")
time.sleep(50/1000)
print(hexlify(serialPort.read(6)))
#serialPort.write(bytearray(unhexlify("AA0401000000")))
time.sleep(50/1000)
imageDataHeader = hexlify(serialPort.read(6))
print(imageDataHeader)
img = []
data = "as"
i = 0
row = []
#for i in range(0,5000/6):
while data != "":
	data =  hexlify(serialPort.read())
	print(str(i) + "). data recieved: " + data)
	if data == "":
		continue
	data = int(data, 16)
	img.append(data)
#	row.append(data)
#	time.sleep(50/1000)
	i+= 1
serialPort.write(bytearray(unhexlify("AA0E0A000100")))
imgarray = np.array(img, dtype=np.uint8)
imgarray.resize((120, 160))

im = Image.fromarray(imgarray, "L")
im.show()
im.save("output.png")
time.sleep(10)
#time.sleep(50/1000)
#print(hexlify(serialPort.read(6)))
#data = ""
#for i in range(0,512):
#	print(i)
#	data += hexlify(serialPort.read(1))
#	time.sleep(50/1000)
#print("recieved image: " + data)
print("end")
serialPort.close()
