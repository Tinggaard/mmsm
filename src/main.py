#!/usr/bin/env python
import sys
import os.path
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt


# load image
def load(file):
    img = cv.imread(file, 1)
    return cv.GaussianBlur(img, (11, 11), 5)


# resize img by scale amount
def resize(img, scale):
    return cv.resize(img, (0,0), fx=scale, fy=scale)


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


# show all imgs, with the ability to zoom and read values
# rather slow function for larger images
def show_imgs(*imgs):
    assert len(imgs) > 0
    fig, ax = plt.subplots(1, len(imgs), figsize=(15, 7), sharex=True, sharey=True,
                                        subplot_kw={'xticks': [], 'yticks': []})

    # single image
    if len(imgs) == 1:
        # greyscale images
        cm = 'gray' if len(imgs[0].shape) <= 2 else None

        # hsv to rgb
        if len(imgs[0].shape) == 3:
            ax.imshow(cv.cvtColor(imgs[0], cv.COLOR_HSV2RGB), cmap=cm)
        else:
            ax.imshow(imgs[0], cmap=cm)

        plt.tight_layout()
        plt.show()
        return

    # multiple images
    for i, im in enumerate(imgs):
        cm = 'gray' if len(im.shape) <= 2 else None

        # hsv to rgb
        if len(im.shape) == 3:
            ax[i].imshow(cv.cvtColor(im, cv.COLOR_HSV2RGB), cmap=cm)
        else:
            ax[i].imshow(im, cmap=cm)

    plt.tight_layout()
    plt.show()


# show multiple windows with trackbars
# works way better (and faster) than show_imgs
def show_with_trackbar(img, rgb, lower_init, upper_init):

    cv.namedWindow('Tracking')
    cv.createTrackbar('Lower Hue', 'Tracking', lower_init[0], 180, nothing)
    cv.createTrackbar('Lower Sat', 'Tracking', lower_init[1], 255, nothing)
    cv.createTrackbar('Lower Val', 'Tracking', lower_init[2], 255, nothing)

    cv.createTrackbar('Upper Hue', 'Tracking', upper_init[0], 180, nothing)
    cv.createTrackbar('Upper Sat', 'Tracking', upper_init[1], 255, nothing)
    cv.createTrackbar('Upper Val', 'Tracking', upper_init[2], 255, nothing)

    while True:

        l_h = cv.getTrackbarPos('Lower Hue', 'Tracking')
        l_s = cv.getTrackbarPos('Lower Sat', 'Tracking')
        l_v = cv.getTrackbarPos('Lower Val', 'Tracking')

        u_h = cv.getTrackbarPos('Upper Hue', 'Tracking')
        u_s = cv.getTrackbarPos('Upper Sat', 'Tracking')
        u_v = cv.getTrackbarPos('Upper Val', 'Tracking')

        lower = (l_h, l_s, l_v)
        upper = (u_h, u_s, u_v)

        mask = in_range(img, lower, upper)

        res = cv.bitwise_and(rgb, rgb, mask=mask)

        cv.imshow('file', img)
        cv.imshow('mask', mask)
        cv.imshow('result', res)

        key = cv.waitKey(1)
        # break on esc or q
        if key == 27 or key == 113:
            break

    cv.destroyAllWindows()
    return cv.bitwise_not(mask) #return inverse mask


# callback function used with cv.createTrackbar function
def nothing(x):
    pass


# shifts hue by 90 (180 deg)
# for some reason, takes forever to complete, so won't use it for now
def shift_hue(hsv):
    # f = lambda v: (v + 90) % 180
    for col in hsv:
        for row in col:
            row[0] = (row[0] + 90) % 180
    return hsv


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


# erode image with kernel size (remove small contours)
def erode(mask, kernel):
    return cv.erode(mask, kernel)


def inv(mask):
    return cv.bitwise_not(mask)


def iterate_contours(contours, hsv):
    blk = black(hsv)

    # [(x,y) - center, color]
    pieces = []

    for no, contour in enumerate(contours):

    # for no, contour in enumerate(contours[7:29], start=7): #7..28 singles
    # for no, contour in enumerate(contours[24:29], start=24): #7..28 singles

        copy = hsv.copy()
        mask = cv.drawContours(blk, [contour], -1, (255), -1)

        cp, ms = crop(contour, copy, mask)
        candy = apply(ms, cp)
        # save(f'singles/{no}', candy)

        hue = [col[0] for row in candy for col in row if col[1] > 100]

        hist, _ = np.histogram(hue, 18, (0,179))
        s = sum(hist)

        # m = cv.mean(candy, mask=ms)
        # mean = [round(i) for i in m[:3]]

        #finding the center
        (x,y), radius = cv.minEnclosingCircle(contour)
        center = (int(x), int(y))



        # yellow hue (10-20 is way bigger than everything else)
        if (hist[1] > (s - hist[1])*2.5) and sum(hist[5:14]) == 0:
            pieces.append(['yellow', center])
            print(f'Found yellow at {center} (img {no})')
            continue

        # red hue (basically only 0-10)
        if hist[0] > sum(hist[1:])*25:
            pieces.append(['red', center])
            print(f'Found red at {center} (img {no})')
            continue

        # green hue (40-70 is strong)
        if sum(hist[4:7]) > s - sum(hist[4:7]):
            pieces.append(['green', center])
            print(f'Found green at {center} (img {no})')
            continue

        # print(mean)
        # print(no)
        # print(hist)

    print(np.array(pieces))



def main():
    f = sys.argv[1]
    img = load(f)
    # img = resize(img, 0.2)
    # save('blur', img)
    hsv, h, s, v = to_hsv(img)
    # save('hue', h)
    # save('sat', s)
    # save('val', v)

    # threshold values for all candy
    lower, upper = (0, 0, 25), (180, 130, 215)

    # mask = show_with_trackbar(hsv, img, lower, upper)
    mask = inv(in_range(hsv, lower, upper))

    #opening
    k = kernel(16)
    open = cv.morphologyEx(mask, cv.MORPH_OPEN, k)
    # save('eroded', open)

    cnt, _ = cv.findContours(open, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = [c for c in cnt if cv.contourArea(c) > 2500]

    antal = len(contours)
    print(f'Fandt {antal} stykker slik')

    # im = cv.drawContours(img, contours, -1, (0,255,0), 3)
    # save('contours', im)

    iterate_contours(contours, hsv)



# main program
if __name__ == '__main__':
    main()
