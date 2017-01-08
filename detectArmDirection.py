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
	


# --------------------------------------------
# Return the intex of the leftmost pixel if
# leftMost = 1, or the rightmost pixel otherwise
# It returns (0, 0) if the image is 
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

	x = 0
	y = 0
	if itemindex != -1:
		x = itemindex;
		y1 = findFirst(1, grayDiff[:, x])
		y2 = findLast(1, grayDiff[:, x])
		y = (int)((y1+y2)/2)
		
		
	return (x, y)


	
