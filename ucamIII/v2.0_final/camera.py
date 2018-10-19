# camera.py
#
# ============================== Description ==========================
#	A beta program used to interface with the uCAM-III CMOS camera.
#
# =============================== Functions ==========================
# 	sync_camera()
#		Purpose: Syncs the camera to a 9600 baud
#		Arguments: None
#		Returns: sync_bit: The hex byte that holds the sync count.
#			Can be used to verify integrity of other communications
# 	init_camera(image_size)
#		Purpose: Configures the camera to take a grayscale raw image
#		Arguments: image_size: The size of the image in pixels.
#			Acceptable Values:
#				"80x60" <--- garbled image
#				"160x120"
#				"128x128" <---- doesn't work
#				"128x96"
#			If an unacceptable value is passed, function will
#			assume "160x120".
#		Returns: None
# 	get_picture()
#		Purpose: takes a picture with settings in get_picture
#		Arguments: image_size: same format as the image_size in
#			 init_camera()
#		Returns: A 1-dimensional list of grayscale picture data,
#		in int() format
#	process_image(img, image_size, mode, file_name)
#		Purpose: Processes the data returned from a picture.
#		Arguments:
#			img: A 1-dimensional list of picture data, int() format
#			image_size: same format as above
#			mode: Type of processing to be applied to the image
#				Possible values:
#				"write out": Saves raw image to a png file
#				"find brightest": Returns x and y coordinates
#					of the brightest pixel
#			file_name: The name of the destination file to be used
#				in "write out". PNG works best.
#				Ex: "picture.png"
#		Returns: Will return an [x,y] coordinate list if a "find ..."
#			command is sent. Will return a 1 if "write_out" is
#			successful, and a 0 if it is not."
#
# ================================= Wiring ==================================
# | Physical Header |    Name   | uCAM port |
# |        2        |     5V    |     5V    |
# |        6        |    GND    |    GND    |
# |        8        | Serial Tx |     Tx    |
# |        10       | Serial Rx |     Rx    |
# |        12       |   GPIO1   |    RES    | (Active LOW)

# External libraries
# PIL and numpy are used to create the png image in process_image()
from PIL import Image
import numpy as np
# libraries for general I/O
import serial
import RPi.GPIO as GPIO
# time is used for serial timing
import time
# binascii is used to create hex strings for the serial communication
from binascii import hexlify, unhexlify

# Initialize the RESET GPIO pin, and
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
# write a HIGH signal to turn off reset
GPIO.output(12, GPIO.HIGH)

# begin serial communication
serialPort = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=.5)

# camera sync function
def sync_camera():
	# sync_bit is the hex number the camera will send when it syncs.
	sync_bit = "00"
	# init delay to 5 msec
	delay = 5
	# sync_string is the sync reply from the camera
	sync_string = ""
	# documentation says try syncing 60 times, increasing delay by 1 msec
	for i in range(0, 60):
		print("Sending sync, try " + str(i))
		# send the sync
		serialPort.write(bytearray(unhexlify('aa0d00000000')))
		string = ""
		time.sleep(delay/1000)
		# read the response from camera
		string = hexlify(serialPort.read(6))
		print("Recieved from cam: " + string)
		# check if we recieved ACK
		if "aa0e0d" in string.lower():
			print("sync recieved! String: " + string)
			sync_string = string
			continue
		# if we recieved ACK, we will then recieve SYNC on the next loop
		if "aa0d00000000" in string and sync_string != "":
			print("Sync ACK: " + string)
			sync_bit = sync_string[6:8]
			print("sending sync ack with bit " + sync_bit + "...")
			# send the ACK with the correct sync number
			serialPort.write(bytearray(unhexlify("AA0E00"+sync_bit+"0000")))
			print("synced!")
			# break the loop
			break
		else:
			sync_string = ""
		delay += 1
	# return the sync bit
	return sync_bit
# init_camera function
def init_camera(image_size):
	# check to see what the requested image size is, then send the init command
	# Command structure:
	# AA0100xxyyzz
	#	xx: Image format: 03 for 8-bit grayscale
	#	yy: Image resolution: set as image_size.
	#	zz: JPEG resolution. Don't care
	if image_size == "80x60":
		serialPort.write(bytearray(unhexlify("AA0100030107")))
		print("sent: AA0100030107")
		time.sleep(50/1000)
		print(hexlify(serialPort.read(6)))
	if image_size == "128x128":
		serialPort.write(bytearray(unhexlify("AA0100030907")))
		print("sent: AA0100030907")
		time.sleep(50/1000)
		print(hexlify(serialPort.read(6)))
	if image_size == "128x96":
		serialPort.write(bytearray(unhexlify("AA0100030B07")))
		print("sent: AA0100030B07")
		time.sleep(50/1000)
		print(hexlify(serialPort.read(6)))
	else:
		serialPort.write(bytearray(unhexlify("AA0100030307")))
		print("sent: AA0100030307")
		time.sleep(50/1000)
		print(hexlify(serialPort.read(6)))
	# ask for UNCOMPRESSED picture
	serialPort.write(bytearray(unhexlify("AA0501000000")))
	print("sent: AA0501000000")
	time.sleep(50/1000)
	print(hexlify(serialPort.read(6)))
	# set sleep timeout to 0
	serialPort.write(bytearray(unhexlify("AA1500000000")))
	print("Sent: AA1500000000")
	time.sleep(50/1000)
	print(hexlify(serialPort.read(6)))
# get picture function
def get_picture(image_size):
	# send the get picture command
	serialPort.write(bytearray(unhexlify("AA0402000000")))
	print("sent: AA0402000000")
	time.sleep(50/1000)
	print(hexlify(serialPort.read(6)))
	time.sleep(50/1000)
	# image data header that I am not sure what do to with yet
	imageDataHeader = hexlify(serialPort.read(6))
	print(imageDataHeader)
	# init the variables used in the loop
	img = []
	data = "as"
	i = 0
	print("Recieving image....")
	# loop until we stop recieving data
	while data != "":
		# read data hex byte one by one, convert to int, then append
		# to the img list
		data =  hexlify(serialPort.read())
		#print(str(i) + "). data recieved: " + data)
		if data == "":
			continue
		data = int(data, 16)
		img.append(data)
		i+= 1
	# use the image_size to verify data integrity
	image_x = int(image_size.split("x")[0])
	image_y = int(image_size.split("x")[1])
	print("image Recieved!")
	if len(img) < image_x * image_y:
		print("WARNING: possibly malformed image")

	# send ACK to camera to put camera to sleep.
	serialPort.write(bytearray(unhexlify("AA0E0A000100")))
	return img
def process_image(img, image_size, mode, img_file):
	if mode.lower() == "write out":
		imgarray = np.array(img, dtype=np.uint8)
		image_x = int(image_size.split("x")[1])
		image_y = int(image_size.split("x")[0])
		imgarray.resize((image_x, image_y))
		im = Image.fromarray(imgarray, "L")
		im.save(img_file)
	elif mode.lower() == "find brightest":
		max_brightness = max(img)
		max_brightness_location = img.index(max(img))
		return([max_brightness, max_brightness_location])
# ACTUAL PROGRAM
sync = sync_camera()
time.sleep(2)
image_size = "160x120"
init_camera(image_size)
img = get_picture(image_size)
process_image(img, image_size, "write out", "output.png")
brightness = process_image(img, image_size, "find brightest", "whatever")
print(brightness)
img[brightness[1]] = 0
process_image(img, image_size, "write out", "output2.png")
print("end")
# close the serial port and cleanup the GPIO
serialPort.close()
GPIO.cleanup()
