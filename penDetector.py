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
			vec = [x2-x1, y2-y1] 
			norm = np.sqrt(vec[0]*vec[0]+vec[1]*vec[1])
			vec[0] = vec[0]/norm
			vec[1] = vec[1]/norm
			coeff = 150
			pt2 = (int(x2+coeff*vec[0]),int(y2+coeff*vec[1]))
			pt1 = (int(x1-coeff*vec[0]),int(y1-coeff*vec[1])) 
			
			tmpFrame = np.zeros((height,width,1), dtype = "uint8")
			cv2.line(tmpFrame,pt1,pt2,20,2)
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
	#	if maxLoc[1] < width-1:
	#		imgCopy[maxLoc[1]+1,maxLoc[0]] = 0
	#	if maxLoc[0] > 0:
	#		imgCopy[maxLoc[1],maxLoc[0]-1] = 0
	#	if maxLoc[0] < height-1:
	#		imgCopy[maxLoc[1],maxLoc[0]+1] = 0
		
	return spotsImg

def frameTreatment(frame, prevFrame):
	frameHeight, frameWidth, nbColors = frame.shape
	frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frameHSL = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
	frameHue = frame[:,:,0]
	frameHSLGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frameLightness = frame[:,:,1]
	frameSaturation = frame[:,:,2]

	diff = cv2.absdiff(frame, prevFrame)
	diffGray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	ret, diffGray = cv2.threshold(diffGray, 10, 255, cv2.THRESH_TOZERO)
	diffGray = cv2.equalizeHist(diffGray)
	ret, diffGrayBin = cv2.threshold(diffGray,68, 255, cv2.THRESH_BINARY)

	frameLaplacian = cv2.Laplacian(frameHSLGray, -1)
	#ret, frameLaplacian = cv2.threshold(frameLaplacian,5, 255, cv2.THRESH_BINARY)
	frameCanny = cv2.Canny(frameGray, threshold1=10, threshold2=150, apertureSize=3)
	frameCannyDiff = cv2.bitwise_and(frameCanny,frameCanny,mask=diffGrayBin) 
	frameLaplacianDiff = cv2.bitwise_and(frameLaplacian,frameLaplacian,mask=diffGrayBin)

	lines = cv2.HoughLinesP(frameLaplacianDiff,1,np.pi/180,threshold=10,minLineLength=10,maxLineGap=1)
#	lines = cv2.HoughLines(diffCanny,1,np.pi/180,threshold=20)
	frameIntersections = intersectionsP(lines, frameHeight, frameWidth)	

	#lines = cv2.HoughLinesP(frameIntersections,1,np.pi/180,threshold=100,minLineLength=10,maxLineGap=10)
	#frameIntersections2 = intersectionsP(lines, frameHeight, frameWidth)
	frameIntersectionsBlur = cv2.GaussianBlur(frameIntersections,(33,33),0)

	backImg = cv2.cvtColor(frameIntersections, cv2.COLOR_GRAY2BGR)
	spotsImg = brightestSpotsImg(frameIntersectionsBlur, 10)
	spotsImg = cv2.add(spotsImg,backImg)
	img = cv2.cvtColor(frameIntersections, cv2.COLOR_GRAY2BGR)
	img[:,:,0] = 0
	#img2 = cv2.cvtColor(frameIntersections2, cv2.COLOR_GRAY2BGR)
	#img = cv2.add(img,img2)
	img=spotsImg
	cv2.imshow('window', img)

def pause():
	while(True):
		key = cv2.waitKey()
		key = key & 0xff
		if key == 32 or key == 27:
			break

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
		frameTreatment(frame, prevFrame)
		
		key = cv2.waitKey(50)
		key = key & 0xFF
		if (key == 27):
			break
		if (key == 32):# espace
			pause()
		prevFrame = frame
video = cv2.VideoCapture('video_stylo.avi')
if (not video.isOpened()):
	print('video file failed to open')
	exit()	
videoLoop(video)
