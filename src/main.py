#!/usr/bin/env python
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
from os import path

# load image
def load(file):
    img = cv2.imread(file, 1)
    return cv2.GaussianBlur(img, (11, 11), 5)


# resize img by scale amount
def resize(img, scale):
    return cv2.resize(img, (0,0), fx=scale, fy=scale)


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
            ax.imshow(cv2.cvtColor(imgs[0], cv2.COLOR_HSV2RGB), cmap=cm)
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
            ax[i].imshow(cv2.cvtColor(im, cv2.COLOR_HSV2RGB), cmap=cm)
        else:
            ax[i].imshow(im, cmap=cm)

    plt.tight_layout()
    plt.show()


# show multiple windows with trackbars
# works way better (and faster) than show_imgs
def show_with_trackbar(img, rgb, lower_init, upper_init):

    cv2.namedWindow('Tracking')
    cv2.createTrackbar('Lower Hue', 'Tracking', lower_init[0], 180, nothing)
    cv2.createTrackbar('Lower Sat', 'Tracking', lower_init[1], 255, nothing)
    cv2.createTrackbar('Lower Val', 'Tracking', lower_init[2], 255, nothing)

    cv2.createTrackbar('Upper Hue', 'Tracking', upper_init[0], 180, nothing)
    cv2.createTrackbar('Upper Sat', 'Tracking', upper_init[1], 255, nothing)
    cv2.createTrackbar('Upper Val', 'Tracking', upper_init[2], 255, nothing)

    while True:

        l_h = cv2.getTrackbarPos('Lower Hue', 'Tracking')
        l_s = cv2.getTrackbarPos('Lower Sat', 'Tracking')
        l_v = cv2.getTrackbarPos('Lower Val', 'Tracking')

        u_h = cv2.getTrackbarPos('Upper Hue', 'Tracking')
        u_s = cv2.getTrackbarPos('Upper Sat', 'Tracking')
        u_v = cv2.getTrackbarPos('Upper Val', 'Tracking')

        lower = (l_h, l_s, l_v)
        upper = (u_h, u_s, u_v)

        mask = in_range(img, lower, upper)

        res = cv2.bitwise_and(rgb, rgb, mask=mask)

        cv2.imshow('file', img)
        cv2.imshow('mask', mask)
        cv2.imshow('result', res)

        key = cv2.waitKey(1)
        # break on esc or q
        if key == 27 or key == 81:
            break

    cv2.destroyAllWindows()


# callback function used with cv2.createTrackbar function
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
    hsv = cv2.cvtColor(new, cv2.COLOR_BGR2HSV)
    hue = hsv[:,:,0]
    sat = hsv[:,:,1]
    val = hsv[:,:,2]

    return hsv, hue, sat, val


# save img to destination
def save(dst, img):
    dir = path.join('../out/', dst + '.jpg')
    cv2.imwrite(dir, img)


# return a mask in the given range over the given image
def in_range(img, lower, upper):
    mask = cv2.inRange(img, lower, upper)
    return mask


# black square size k*k
def kernel(k):
    return cv2.getStructuringElement(cv2.MORPH_RECT,(k,k))


# erode image with kernel size (remove small contours)
def erode(mask, kernel):
    return cv2.erode(mask, kernel)


# green mask
def mask_green(img, k=75):
    m = in_range(img, (20, 0, 0), (90, 255, 255))
    save('early', m)
    return erode(m, kernel(k))


# red mask ish
def mask_tmp(img, k=25):
    m1 = in_range(img, (0, 150, 150), (20, 255, 255))
    m2 = in_range(img, (160, 150, 150), (180, 255, 255))
    m = cv2.bitwise_or(m1, m2)
    save('early', m)
    return erode(m, kernel(k))



# main program
if __name__ == '__main__':
    f = sys.argv[1]
    img = load(f)
    img = resize(img, 0.2)
    # save('blur', img)
    hsv, h,s,v = to_hsv(img)
    # save('hue', h)
    # save('sat', s)
    # save('val', v)

    # threshold values for all candy
    lower, upper = (0, 0, 25), (180, 130, 215)

    show_with_trackbar(hsv, img, lower, upper)



    # m = mask_tmp(hsv)
    #
    # # get centers of contours
    # retval, labels, stats, centroids = cv2.connectedComponentsWithStats(m, 4, cv2.CV_32S)
    #
    # for x,y in centroids[1:]:
    #     # circle around found contour
    #     cv2.circle(m,(int(x),int(y)),200,255,2)
    #     save('mask', m)
    # # print(retval) # antal
    # show(hsv, h, s, v, m)
