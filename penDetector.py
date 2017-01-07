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


def intersectionsP(lines, height, width):
	frameIntersectionsP = np.zeros((height,width,1), dtype = "uint8") 
	if lines is not None:
		for line in lines:
			x1,y1,x2,y2 = line[0]
			vec = (x2-x1, y2-y1) 
			pt2 = (x2+3*vec[0],y2+3*vec[1])
			pt1 = (x1-3*vec[0],y1-3*vec[1]) 
			
			tmpFrame = np.zeros((height,width,1), dtype = "uint8")
			cv2.line(tmpFrame,pt1,pt2,10,2)
			frameIntersectionsP = cv2.add(frameIntersectionsP, tmpFrame)
	return frameIntersectionsP

def brightestSpotsImg(img, nbSpots):
	imgCopy = img.copy()
	height, width = img.shape
	spotsImg = np.zeros((height,width,3), dtype = "uint8")
	for i in range(nbSpots):
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(imgCopy)
		cv2.circle(spotsImg, maxLoc, 10, (0,255,0), 2)
		imgCopy[maxLoc[1],maxLoc[0]] = 0
		if maxLoc[1] > 0:
			imgCopy[maxLoc[1]-1,maxLoc[0]] = 0
		if maxLoc[1] < width:
			imgCopy[maxLoc[1]+1,maxLoc[0]] = 0
		if maxLoc[0] > 0:
			imgCopy[maxLoc[1],maxLoc[0]-1] = 0
		if maxLoc[0] < height:
			imgCopy[maxLoc[1],maxLoc[0]+1] = 0
		
	return spotsImg

# --------------------------------------------
# Find the first value upper a minimum value in
# an array and return the index, or -1 if there
# is no results
# --------------------------------------------
def find_first(mini_value, array):
	size = len(array)
	for i in range(size):
		if  array[i] >= mini_value:
			return i
	return -1

# --------------------------------------------
# Return the intex of the leftest (ca se dit ca ???)
# value in a gray image or (0, 0) is the image is 
# totally black
# --------------------------------------------
def leftestPoint(grayDiff):
	hProj = sum(grayDiff,2)  #horizontal projection
	itemindex = find_first(5, hProj)
	x = 0
	y = 0
	if itemindex != -1:
		x = itemindex;
		y = find_first(5, grayDiff[:, x])
		
	return (x, y)
	

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
	# binarisation of the gray difference
	ret, diffGray = cv2.threshold(diffGray, 10, 255, cv2.THRESH_TOZERO)

	# --------- to remove, c pas bô ------------
	coordonates = leftestPoint(diffGray)
	imgCopy2 = np.zeros((frameHeight,frameWidth,3), dtype = "uint8")
	imgCopy2 = frame.copy()
	cv2.circle(imgCopy2, coordonates, 10, (0,255,0), 2)

	cv2.imshow('imgCopy2', imgCopy2)
	# ------------------------------------------

	# histogram equalisation
	diffGray = cv2.equalizeHist(diffGray)
	ret, diffGrayBin = cv2.threshold(diffGray,68, 255, cv2.THRESH_BINARY)

	frameDiff = cv2.bitwise_and(frame,frame,mask=diffGrayBin) 
	diffCanny = cv2.Canny(frameDiff, threshold1=100, threshold2=500, apertureSize=3)

#	lines = cv2.HoughLinesP(diffCanny,1,np.pi/180,threshold=20,minLineLength=10,maxLineGap=5)
	lines = cv2.HoughLines(diffCanny,1,np.pi/180,threshold=30)
	
	frameIntersections = intersections(lines, frameHeight, frameWidth)	
	
	frameIntersectionsBlur = cv2.GaussianBlur(frameIntersections,(33,33),0)
	spotsImg = brightestSpotsImg(frameIntersectionsBlur, 10)
	spotsImg = cv2.add(spotsImg, frame)
	img=spotsImg
	cv2.imshow('window', spotsImg)


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
	cv2.namedWindow('window')

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
