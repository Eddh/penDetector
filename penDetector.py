import numpy as np
import cv2
import argparse
from kallman import Kallman

from lineDetection import *
from detectArmDirection import *


# -----------------------------------
# Treate the current frame, using
# the previous frame
# -----------------------------------
def frameTreatment(frame, prevFrame):
	# initialisation
	frameHeight, frameWidth, nbColors = frame.shape
	frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frameHSL = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
	frameHue = frame[:,:,0]
	frameLightness = frame[:,:,1]
	frameSaturation = frame[:,:,2]

	# the difference between the current frame and the previous frame
	diff = cv2.absdiff(frame, prevFrame)
	diffGray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	# thresholding of the gray difference
	ret, diffGray = cv2.threshold(diffGray, 20, 255, cv2.THRESH_TOZERO)
	
	# extract dark pixel
	binarizedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	ret, binarizedFrame = cv2.threshold(binarizedFrame, 80, 255, cv2.THRESH_BINARY_INV)

	# we remove the white parts 
	diffGray = cv2.min(binarizedFrame, diffGray)


	# detect if there is an arm in the image and his direction
	(res, armAngle) = detectArmAngle(diffGray, frameWidth, frameHeight)

	imgCopy2 = np.zeros((frameHeight,frameWidth,3), dtype = "uint8")
	imgCopy2 = frame.copy()


	coordinates = (-1, -1)

	if res:
		armPoint = ((int)(frameWidth/2)+(int)(frameWidth/2*np.cos(armAngle)),(int)(frameHeight/2)+(int)(frameWidth/2*np.sin(armAngle)))
		cv2.line(imgCopy2,((int)(frameWidth/2),(int)(frameHeight/2)),armPoint,5,2)	
	
		# compute coordinates
		coordinates = findFarthestPoint(diffGray, frameWidth, frameHeight, armPoint)
	

		cv2.circle(imgCopy2, coordinates, 10, (0,255,0), 2)

	cv2.imshow('imgCopy2', imgCopy2)
	cv2.imshow('diffGray', diffGray)

	return coordinates

	# histogram equalisation
	#diffGray = cv2.equalizeHist(diffGray)
	#ret, diffGrayBin = cv2.threshold(diffGray,68, 255, cv2.THRESH_BINARY)

	#frameDiff = cv2.bitwise_and(frame,frame,mask=diffGrayBin) 
	#diffCanny = cv2.Canny(frameDiff, threshold1=100, threshold2=500, apertureSize=3)

	#lines = cv2.HoughLines(diffCanny,1,np.pi/180,threshold=30)
	
	#frameIntersections = intersections(lines, frameHeight, frameWidth)	
	
	#frameIntersectionsBlur = cv2.GaussianBlur(frameIntersections,(33,33),0)
	#spotsImg = brightestSpotsImg(frameIntersectionsBlur, 10)
	#spotsImg = cv2.add(spotsImg, frame)
	#img=spotsImg
	#cv2.imshow('window', spotsImg)

# -----------------------------------
# Write the ouput image
# -----------------------------------
def computeOutputImage(pointCoordinates, frameHeight, frameWidth, fileName):
	# the maximum distance between points
	maxDist = 50

	# create the ouput image
	outputImage = np.zeros((frameWidth,frameHeight,1), dtype = "uint8")
	outputImage[:] = 255

	for i in range(len(pointCoordinates)):
		if i>0:
			p1 = pointCoordinates[i-1]
			p2 = pointCoordinates[i]
			dist = np.sqrt((p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]))
			if dist<=maxDist:
				cv2.line(outputImage,p1,p2,10,2)

	cv2.imwrite(fileName, outputImage)

# -----------------------------------
# infinite loop while the user doesn't
# press espace or escape
# -----------------------------------
def pause():
	while(True):
		key = cv2.waitKey()
		key = key & 0xff
		if key == 32 or key == 27:
			break

# -----------------
# Main program loop
# -----------------
def videoLoop(video):
	# initialisation
	frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
	frameWidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
	frameHeight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
	prevFrame = np.zeros((frameHeight, frameWidth, 3), dtype = "uint8")
	frame = np.zeros((frameHeight, frameWidth, 3), dtype = "uint8")

	# read the first frame
	ret, prevFrame = video.read()

	Qk = np.array([[0.001, 0  , 0  , 0  ],
					[0 , 0.001, 0  , 0  ],
					[0 , 0  , 0.01, 0  ],
					[0 , 0  , 0  , 0.01]], dtype='Float64') 

	Rk = np.array([[0.2, 0  , 0  , 0  ],
					[0 , 0.2, 0  , 0  ],
					[0 , 0  , 0.3, 0  ],
					[0 , 0  , 0  , 0.3]], dtype='Float64')

	Fk = np.array([[1  , 0  , 0  , 0  ],
					[0 , 1  , 0  , 0  ],
					[0 , 0  , 1  , 0  ],
					[0 , 0  , 0  , 1  ]], dtype='Float64')

	kallmanFilter = Kallman(4, np.identity(4), Qk, Fk)

	PkInitial = np.array([[0.5, 0  , 0  , 0  ],
						   [0 , 0.5, 0  , 0  ],
						   [0 , 0  , 0.5, 0  ],
						   [0 , 0  , 0  , 0.5]], dtype='Float64')
	vX = 0
	vY = 0
	print(np.asarray((0,0)))
	kallmanFilter.initialize(np.asarray((frameWidth/2,frameHeight/2, vX, vY)), PkInitial)
	
	pointCoordinates = []
	pointCoordinatesKallman = []

	deltaT = 1

	while(video.isOpened()):
		ret, frame = video.read()
		if (not ret):
			print('end of video')
			
			computeOutputImage(pointCoordinates, frameWidth, frameHeight, 'out.png')
			computeOutputImage(pointCoordinatesKallman, frameWidth, frameHeight, 'out2.png')
			
			break

		coordinates = frameTreatment(frame, prevFrame)
		print(coordinates)
		if coordinates != (-1, -1):
			if len(pointCoordinates) > 1:
				vX = pointCoordinatesKallman[len(pointCoordinates)-2][0] - pointCoordinatesKallman[len(pointCoordinates)-1][0]
				vY = pointCoordinatesKallman[len(pointCoordinates)-2][1] - pointCoordinatesKallman[len(pointCoordinates)-1][1]

			Fk = np.array([[1 , 0  , deltaT  , 0  ],
						   [0 , 1  , 0  , deltaT  ],
						   [0 , 0  , 1  , 0  ],
					       [0 , 0  , 0  , 1  ]], dtype='Float64')
			kallmanFilter.setFk(Fk)
			zk = (coordinates[0], coordinates[1], vX, vY)
			retKallman = kallmanFilter.update(np.asarray(zk), Rk)
			coordinatesKallman = (int(retKallman[0]), int(retKallman[1]))
			print('wat')
			print(coordinatesKallman)
			frameCopy = frame.copy()
			cv2.circle(frameCopy, coordinatesKallman, 10, (0,0,255), 2)
			cv2.imshow('kallman', frameCopy)
			
			
			pointCoordinates.append(coordinates)
			pointCoordinatesKallman.append(coordinatesKallman)		

			
		key = cv2.waitKey(50)
		key = key & 0xFF
		if (key == 27):# escape key
			break# end the program
		if (key == 32):# espace key
			pause()# pause the program
		prevFrame = frame


	
video = cv2.VideoCapture('video_stylo.avi')
if (not video.isOpened()):
	print('video file failed to open')
	exit()	
videoLoop(video)
