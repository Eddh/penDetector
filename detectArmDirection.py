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
			lastIndex = i
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
	cv2.imshow('grayDiff', grayDiff)

	leftMostPixelColumn = grayDiff[:, 0]
	rightMostPixelColumn = grayDiff[:, frameWidth-1]

	countLeft = countValues(10, leftMostPixelColumn)
	countRight = countValues(10, rightMostPixelColumn)

	if countLeft == 0 and countRight == 0:
		return -1
	elif countLeft > countRight:
		return 0
	else :
		return 1
	

# --------------------------------------------
# Return the intex of the leftmost
# value in a gray image or (0, 0) is the image is 
# totally black
# --------------------------------------------
def lefmostPoint(grayDiff):
	hProj = sum(grayDiff,2)  #horizontal projection
	itemindex = findFirst(5, hProj)
	x = 0
	y = 0
	if itemindex != -1:
		x = itemindex;
		y = findFirst(5, grayDiff[:, x])
		
	return (x, y)

# --------------------------------------------
# Return the intex of the leftmost
# value in a gray image or (0, 0) is the image is 
# totally black
# --------------------------------------------
def rightmostPoint(grayDiff):
	hProj = sum(grayDiff,2)  #horizontal projection
	itemindex = findLast(5, hProj)
	x = 0
	y = 0
	if itemindex != -1:
		x = itemindex;
		y = findFirst(5, grayDiff[:, x])
		
	return (x, y)
	
