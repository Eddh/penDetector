import numpy as np
import cv2
import argparse
import kallman


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
	ret, diffGray = cv2.threshold(diffGray, 10, 255, cv2.THRESH_TOZERO)
	
	# detect if there is an arm in the image and his direction
	armDirection = detectArmDirection(diffGray, frameWidth)
	print(armDirection)


	imgCopy2 = np.zeros((frameHeight,frameWidth,3), dtype = "uint8")
	imgCopy2 = frame.copy()

	if armDirection == 0:
		coordonates = rightmostPoint(diffGray, frameWidth)
		cv2.circle(imgCopy2, coordonates, 10, (0,255,0), 2)
	elif armDirection == 1:
		coordonates = lefmostPoint(diffGray)
		cv2.circle(imgCopy2, coordonates, 10, (0,255,0), 2)

	cv2.imshow('imgCopy2', imgCopy2)

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
# infinite loop while the user doen't
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
	

	while(video.isOpened()):
		ret, frame = video.read()
		if (not ret):
			print('end of video')
			break
		frameTreatment(frame, prevFrame)
		
		key = cv2.waitKey(50)
		key = key & 0xFF
		if (key == 27):# escape
			break# end the program
		if (key == 32):# espace
			pause()
		prevFrame = frame


video = cv2.VideoCapture('video_stylo.avi')
if (not video.isOpened()):
	print('video file failed to open')
	exit()	
videoLoop(video)
