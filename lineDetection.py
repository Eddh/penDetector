
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
