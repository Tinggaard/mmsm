#!/usr/bin/env python
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path


# load image
def load(file):
    img = cv.imread(file, 1)
    return cv.GaussianBlur(img, (11, 11), 5)


# Convert bgr img to hsv
def to_hsv(img):
    new = img.copy() # maybe not needed?
    hsv = cv.cvtColor(new, cv.COLOR_BGR2HSV)
    hue = hsv[:,:,0]
    sat = hsv[:,:,1]
    val = hsv[:,:,2]

    return hsv, hue, sat, val


# save img to destination
def save(dst, img):
    dir = os.path.join('../out/', dst + '.jpg')
    cv.imwrite(dir, img)


# return a mask in the given range over the given image
def in_range(img, lower, upper):
    mask = cv.inRange(img, lower, upper)
    return mask


# black square size k*k
def kernel(k):
    # return np.ones(k, k)
    return cv.getStructuringElement(cv.MORPH_RECT,(k,k))


# erode image with kernel size (remove small contours)
def erode(mask, kernel):
    return cv.erode(mask, kernel)


# green mask
def mask_green(img, k=75):
    m = in_range(img, (20, 0, 0), (90, 255, 255))
    return erode(m, kernel(k))


# main program
if __name__ == '__main__':
    f = sys.argv[1]
    img = load(f)
    hsv, h,s,v = to_hsv(img)

    m = mask_green(hsv)

    # get centers of contours
    retval, labels, stats, centroids = cv.connectedComponentsWithStats(m, 4, cv.CV_32S)

    for x,y in centroids[1:]:
        # circle around found contour
        cv.circle(m,(int(x),int(y)),200,255,2)
    save('mask', m)

    print(retval-1) # antal
