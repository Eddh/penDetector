import numpy as np
import cv2
import argparse

def intersections(lines, height, width):
	frameIntersections = np.zeros((height,width,1), dtype = "uint8") 
	if lines is not None:
		for line in lines:
			rho,theta = line[0]
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			tmpFrame = np.zeros((height,width,1), dtype = "uint8")
					
			cv2.line(tmpFrame,(x1,y1),(x2,y2),5,2)	
			frameIntersections = cv2.add(frameIntersections, tmpFrame)
	return frameIntersections
def brightestSpotsImg(img, nbSpots):
	imgCopy = img.copy()
	height, width = img.shape
	spotsImg = np.zeros((height,width,3), dtype = "uint8")
	for i in range(nbSpots):
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(imgCopy)
		cv2.circle(spotsImg, maxLoc, 10, (0,255,0), 2)
		imgCopy[maxLoc[1],maxLoc[0]] = 0
		
	return spotsImg

def videoLoop(video):
	frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
	frameWidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
	frameHeight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
	prevFrame = np.zeros((frameHeight, frameWidth, 3), dtype = "uint8")
	frame = np.zeros((frameHeight, frameWidth, 3), dtype = "uint8")
	ret, prevFrame = video.read()
	cv2.namedWindow('window')	

	while(video.isOpened()):		
		ret, frame = video.read()
		if (not ret):
			print('end of video')
			break
		frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		diff = cv2.absdiff(frame, prevFrame)
		diffGray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
		ret, diffBin = cv2.threshold(diffGray, 10, 255, cv2.THRESH_BINARY)
		diffCanny = cv2.Canny(diffGray, 10, 200, 10)
		prevFrame = frame

		lines = cv2.HoughLines(diffCanny,1,np.pi/180,25)
		frameIntersections = intersections(lines, frameHeight, frameWidth)	
		frameIntersectionsBlur = cv2.GaussianBlur(frameIntersections,(33,33),0)
		spotsImg = brightestSpotsImg(frameIntersectionsBlur, 3)
		spotsImg = cv2.add(spotsImg, diff)
		img = spotsImg
		cv2.imshow('window', img)

		key = cv2.waitKey(50)
		key = key & 0xFF
		if (key == 27):
			break

video = cv2.VideoCapture('video_stylo.avi')
if (not video.isOpened()):
	print('video file failed to open')
	exit()	
videoLoop(video)
