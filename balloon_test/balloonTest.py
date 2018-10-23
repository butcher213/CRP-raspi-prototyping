#!/usr/bin/python
import numpy as np
import cv2
import time
from os import listdir
boundaries = ([(100,0,0), (255,255,255)],
	    [(0,100,0), (255,255,255)],
	    [(0,0,100), (255,255,255)])
# get the list of images from the folder
images = listdir("eaglesat_balloon_data")
max_pixel = 0
#print(images)
commonMask = ""
commonMax = ""
compiledData = "Image; Interaction count; Interaction Area; length of interaction; width of interaction; location x; location y; average rgb;  max rgb\n"
j = 0
for imageFileName in images:
	if ".png" not in imageFileName and ".jp" not in imageFileName:
		continue
	print("processing image " +str(j))
	j += 1
#	imageFile = open("eaglesat_balloon_data/" + imageFileName, 'rb')
#	imageData = imageFile.read()
#	imageFile.close()
#	imageArray = np.fromstring(imageData, dtype='uint8')
	imageRaw = cv2.imread("eaglesat_balloon_data/" + imageFileName)
	max_pixel = np.amax([np.amax(imageRaw[:,:,0]), np.amax(imageRaw[:,:,1]), np.amax(imageRaw[:,:,2])])
#	print(imageFileName + ":" + str(max_pixel))
#	if int(max_pixel) > 120:
#		cv2.imshow("Bright image", imageRaw)
#		cv2.waitKey(0)
#	imageRaw = cv2.imdecode(imageArray, cv2.IMREAD_UNCHANGED)
#	imageRaw = cv2.resize(imageArray, (640, 480))
#	imageRaw = cv2.GaussianBlur(imageRaw, (11,11), 1)
	if 1 == 1:
		mask = ""
		for boundary in boundaries:
			lower = np.array(boundary[0], dtype= "uint8")
			upper = np.array(boundary[1], dtype= "uint8")		
			singleMask = cv2.inRange(imageRaw, lower, upper)
			if mask != "":
				mask = cv2.bitwise_or(mask, singleMask)
			else:
				mask = singleMask

		maskedImage = cv2.bitwise_and(imageRaw, imageRaw, mask=mask)
		im, contours, heirarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#		print(contours[0])
		areas = ""
		coords = ""
		dimensions = ""
		colors = []
		if 1 == 1:
			for contour in contours:
				contour = np.array(contour).astype(np.int32)
				areas = str(cv2.contourArea(contour))
				y,x,height, width = cv2.boundingRect(contour)
#				coords = "(" + str(x) + ", " + str(y) + "), "
				colors = imageRaw[x:x+width, y:y+height, :][0]
#				mask[x-5:x,y-5:y] = 255
#				dimensions = "(" + str(width) + ", " + str(height) + 
				avg_rgb = [0,0,0]
				max_rgb = [0,0,0]
				i = 0
				for color in colors:
					if color[0] < 100 and color[1] < 100 and color[2] < 100:
						continue
					if color[0] > max_rgb[0]:
						max_rgb[0] = color[0]				
					if color[1] > max_rgb[1]:
						max_rgb[1] = color[1]				
					if color[2] > max_rgb[2]:
						max_rgb[2] = color[2]
					avg_rgb[0] += color[0]
					avg_rgb[1] += color[1]
					avg_rgb[2] += color[2]
					i += 1
				avg_rgb = "(" + str(avg_rgb[0]/i) + ", " + str(avg_rgb[1]/i) + ", " + str(avg_rgb[2]/i) + ")" 
				max_rgb = "(" + str(max_rgb[0]) + ", " + str(max_rgb[1]) + ", " + str(max_rgb[2]) + ")"
				compiledData += imageFileName + "; " + str(len(contours)) + "; " + areas + "; " + str(width) + "; " + str(height) + "; " + str(x) + "; " + str(y) + "; \"" + avg_rgb + "\"; \"" + max_rgb + "\"\n"
		else:
			print(len(contours))
		if len(areas) != 0:
			a = 0
		#	print("Interaction in " + imageFileName + ":" )
		#	print("\tareas: " + str(areas))
		#	print("\tcoordinates: " + str(coords))
		#	print("\tdimensions: " + str(dimensions))
		#	print("\tColors: " + str(colors))
		#	color = cv2.resize(colors[0], (dimensions[0][0] * 100, dimensions[0][1] * 100))
			
		if commonMax == "":
			commonMax = imageRaw
		else:
			commonMax = cv2.add(commonMax, maskedImage)
	else:
		print("Error on image: " + imageFileName)
#pixels = np.sum(commonMask)
#print(pixels)
file = open("processedData.ssv", "w")
file.write(compiledData)
file.close()
commonMax = cv2.resize(commonMax, (1920, 1080))
cv2.imshow("mask", commonMax)
cv2.waitKey(0)
