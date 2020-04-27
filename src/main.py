#!/usr/bin/env python
import sys
import serial
import time
import os.path
import cv2 as cv
import numpy as np


# load image
def load(file):
    img = cv.imread(file, 1)
    return cv.GaussianBlur(img, (11, 11), 5)


# black image at the size of im
def black(im):
    return np.zeros(im.shape[0:2], np.uint8)


# taken from my earlier project:
# https://github.com/Tinggaard/set-solver/blob/alpha/cards.py#L35
def crop(cnt, *images):
    """Crop images into smaller bits, making it easier on the CPU usage"""
    assert images is not None

    #Checking that all are in fact images
    if not all(isinstance(item, np.ndarray) for item in images):
        raise TypeError('"*images" must be nust be of type: "numpy.ndarray"')

    #Returning the cropped images

    reference_y, reference_x = images[0].shape[:2]

    x,y,w,h = cv.boundingRect(cnt)

    #Ading offset of 2 pixels, so the contours still work properly
    #Making if else statements, to prevent errors in indexing
    y1 = y-2 if 2 < y else 0
    x1 = x-2 if 2 < x else 0
    y2 = y+h+2 if y+h+2 < reference_y else None
    x2 = x+w+2 if x+w+2 < reference_x else None

    return [img[y1:y2, x1:x2] for img in images]


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
    return cv.getStructuringElement(cv.MORPH_ELLIPSE,(k,k))


def apply(mask, img):
    return cv.bitwise_and(img, img, mask=mask)


def inv(mask):
    return cv.bitwise_not(mask)


def iterate_contours(contours, hsv):
    blk = black(hsv)

    # [(x,y) - center, color]
    pieces = []

    for no, contour in enumerate(contours):

    # for no, contour in enumerate(contours[7:29], start=7): #7..28 singles
    # for no, contour in enumerate(contours[12:13], start=12): #7..28 singles

        # mask image
        copy = hsv.copy()
        mask = cv.drawContours(blk, [contour], -1, (255), -1)

        # cropped
        cp, ms = crop(contour, copy, mask)
        candy = apply(ms, cp)
        # save(f'singles/{no}', candy)

        # hues as with sat over 100
        hue = [col[0] for row in candy for col in row if col[1] > 100]

        # histogram of hues
        hist, _ = np.histogram(hue, 18, (0,179))
        s = sum(hist)

        #finding the center
        (x,y), radius = cv.minEnclosingCircle(contour)
        center = (int(x), int(y))

        # rectangle around contour (aspect ratio)
        rect = cv.minAreaRect(contour)
        box = cv.boxPoints(rect)
        box = np.int0(box)

        x1, y1 = box[0,0], box[0,1]
        x2, y2 = box[1,0], box[1,1]
        x3, y3 = box[2,0], box[2,1]

        #Calculates the length of the hypothenus of a triangle
        s1 = np.hypot(x2-x1, y2-y1)
        s2 = np.hypot(x3-x2, y3-y2)

        # aspect ratio
        a = max((s1, s2)) / min((s1, s2))

        # yellow hue (10-20 is way bigger than everything else)
        if (hist[1] > (s - hist[1])*2.5) and sum(hist[5:14]) == 0:
            pieces.append(['yellow', center])
            continue

        # red hue (basically only 0-10)
        if hist[0] > sum(hist[1:])*25:
            pieces.append(['red', center])
            continue

        # green hue (40-70 is strong)
        if sum(hist[4:7]) > s - sum(hist[4:7]):
            pieces.append(['green', center])
            continue

        # laber larve (aspect ratio over 2:1)
        if a > 2:
            pieces.append(['larve', center])
            continue

    return np.array(pieces)


def handle_input(colors):
    print('Choose a candy to pick up')
    print('Available values are: yellow, red, green, larve (or exit)')
    s = input('> ').strip().lower()

    if s == 'exit':
        sys.exit(0)

    if s == 'yellow':
        x = [c[1] for c in colors if c[0] == 'yellow']
        print(f'Found {len(x)} pieces of that choice')
        return x

    if s == 'red':
        x = [c[1] for c in colors if c[0] == 'red']
        print(f'Found {len(x)} pieces of that choice')
        return x

    if s == 'green':
        x = [c[1] for c in colors if c[0] == 'green']
        print(f'Found {len(x)} pieces of that choice')
        return x

    if s == 'larve':
        x = [c[1] for c in colors if c[0] == 'larve']
        print(f'Found {len(x)} pieces of that choice')
        return x

    print('Input not understood, try again')
    handle_input(colors)


def communicator(pieces):
    # port to write to
    # may change from machine to machine depending on port
    port = '/dev/ttyS0'

    # Arduino
    try:
        ard = serial.Serial(port, 9600, timeout=5)
    except:
        print('Could not connect to the Arduino')
        print('Prentending to write...')
        for candy in pieces:
            print(f'Sending the arm to coordinate: {candy}')
        return

    # iterate locations
    for candy in pieces:
        ard.flush()
        # only write x coordinate, as they are on a row (2D)
        ard.write(str(candy[0]))
        time.sleep(10)

        # response
        msg = ard.read(ard.inWaiting())
        print(msg)


def main():
    f = sys.argv[1]
    img = load(f)
    print('Loaded image')
    hsv, h, s, v = to_hsv(img)

    # threshold values for all candy
    lower, upper = (0, 0, 25), (180, 130, 215)

    # mask creation
    mask = inv(in_range(hsv, lower, upper))

    #opening
    k = kernel(16)
    open = cv.morphologyEx(mask, cv.MORPH_OPEN, k)

    # finding the contours
    cnt, _ = cv.findContours(open, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = [c for c in cnt if cv.contourArea(c) > 2500] #size sorting

    # count
    antal = len(contours)
    print(f'Found {antal} pieces of candy')

    print('Processing image')
    colors = iterate_contours(contours, hsv)

    # get user input
    pieces = handle_input(colors)

    # communicate with Arduino
    communicator(pieces)


# main program
if __name__ == '__main__':
    main()
