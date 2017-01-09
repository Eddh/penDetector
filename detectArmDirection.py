import numpy as np
import cv2
import argparse

# --------------------------------------------
# Find the first value upper a minimum value in
# an array and return the index, or -1 if there
# is no results
# --------------------------------------------
def findFirst(threshold, array):
	size = len(array)
	for i in range(size):
		if  array[i] >= threshold:
			return i
	return -1

# --------------------------------------------
# Find the last value upper a minimum value in
# an array and return the index, or -1 if there
# is no results
# --------------------------------------------
def findLast(threshold, array):
	size = len(array)
	lastValue = 0;
	lastIndex = -1;
	for i in range(size):
		if  array[i] < threshold and lastValue>=threshold:
			lastIndex = i-1
		lastValue = array[i]
	return lastIndex

# --------------------------------------------
# Count de values in an array that are
# greater or equal than a minimum value
# --------------------------------------------
def countValues(threshold, array):
	size = len(array)
	values = 0
	for i in range(size):
		if  array[i] >= threshold:
			values = values+1
	return values

# --------------------------------------------
# Return -1 if there is no arm detected,
# return 0 if the arm comes from the left
# return 1 if the arm comes from the right
# --------------------------------------------
#
def detectArmDirection(grayDiff, frameWidth):
	
	# we sum the pixel in the left and the right part of the frame
	countLeft = 0
	countRight = 0
	for i in range((int)(frameWidth/2)):
		countLeft += sum(grayDiff[:, 0+i])
		countRight += sum(grayDiff[:, frameWidth-1-i])

	threshold = 10
	if countLeft < threshold and countRight < threshold:
		return -1
	elif countLeft > countRight:
		return 0
	else :
		return 1
	

def detectArmAngle(grayDiff, frameWidth, frameHeight):
	globalAngle = 0;
	detectedPixel = 0;
	found = False

	#top side
	y=0
	for x in range(frameWidth):
		if grayDiff[y, x]>0:
			angle = np.arctan2(y-frameHeight/2,x-frameWidth/2)
			if angle > np.pi/2:
				angle -= 2*np.pi
			globalAngle += angle
			detectedPixel += 1
	#left side
	x=0
	for y in range(frameHeight):
		if grayDiff[y, x]>0:
			angle = np.arctan2(y-frameHeight/2,x-frameWidth/2)
			if angle > np.pi/2:
				angle -= 2*np.pi
			globalAngle += angle
			detectedPixel += 1
	#bot side
	y=frameHeight-1
	for x in range(frameWidth):
		if grayDiff[y, x]>0:
			angle = np.arctan2(y-frameHeight/2,x-frameWidth/2)
			if angle > np.pi/2:
				angle -= 2*np.pi
			globalAngle += angle
			detectedPixel += 1
	#right side
	x=frameWidth-1
	for y in range(frameHeight):
		if grayDiff[y, x]>0:
			angle = np.arctan2(y-frameHeight/2,x-frameWidth/2)
			if angle > np.pi/2:
				angle -= 2*np.pi
			globalAngle += angle
			detectedPixel += 1
	
	if detectedPixel > 0:
		globalAngle /= detectedPixel
		found = True

	return (found, globalAngle)


def applyRotToCoordinates(imageAngle, rotatedImage, coordinates):

	height, width = rotatedImage.shape[:2]
	imageCenter = (width/2, height/2)

	diffx = coordinates[0]-imageCenter[0]
	diffy = coordinates[1]-imageCenter[1]

	#y axis is inverted
	diffy *= -1

	dist = np.sqrt(diffx*diffx + diffy*diffy)
	
	coordinateAngle = np.arctan2(diffy,diffx)

	
	angleAfterRotation = coordinateAngle-imageAngle
	#print(coordinateAngle)


	rotatedCoordinates = (int(imageCenter[0]+dist*np.cos(angleAfterRotation)), int(imageCenter[1]-dist*np.sin(angleAfterRotation)))
	return rotatedCoordinates
	

def rotateImage(image, radiantAngle):
	height, width = image.shape[:2]
	imageCenter = (width/2, height/2)

	angleDegree = radiantAngle / np.pi * 180
	rotationMatrix = cv2.getRotationMatrix2D(imageCenter, angleDegree, 1)
	
	absCos = np.abs(rotationMatrix[0, 0])
	absSin = np.abs(rotationMatrix[0, 1])

	rotatedImage = cv2.warpAffine(image, rotationMatrix, (width, height))

	return (rotatedImage, rotationMatrix)
	

def findFarthestPoint(diffGray, frameWidth, frameHeight, point):

	coordinates = point
	farthestDist = 0
	for x in range(frameWidth):
		for y in range(frameHeight):
			if diffGray[y, x] > 0:
				dist = (x-point[0])*(x-point[0]) + (y-point[1])*(y-point[1])
				if dist>farthestDist:
					coordinates=(x, y)
					farthestDist = dist
	return coordinates


	


# --------------------------------------------
# Return the intex of the leftmost pixel if
# leftMost = 1, or the rightmost pixel otherwise
# It returns (-1, -1) if the image is 
# totally black
# --------------------------------------------
def extremumPoint(grayDiff, leftMost):
	hProj = sum(grayDiff,2)  #horizontal projection
	
	thresholdValue = 100 
	itemindex = -1
	if leftMost == 1:
		itemindex = findFirst(thresholdValue, hProj)

	else:
		itemindex = findLast(thresholdValue, hProj)

	x = -1
	y = -1
	if itemindex != -1:
		x = itemindex;
		y1 = findFirst(1, grayDiff[:, x])
		y2 = findLast(1, grayDiff[:, x])
		y = (int)((y1+y2)/2)
		
		
	return (x, y)


	
