#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 23 March 2014.
@author: Eugene Dvoretsky

Microrecoreder. Video recording with micro-manager and opencv.

Provides information about buffer capacity.

NB! In development: properly work non guarantee.
"""

import time
import numpy as np
import cv2
import MMCorePy

DEVICE = ['Camera', 'DemoCamera', 'DCam']
# DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = ['Camera', 'BaumerOptronic', 'BaumerOptronic']
OUT_VIDEO = 'output.avi'


def set_mmc_resolution(mmc, width, height):
    """Select rectangular ROI in center of the frame.
    """
    x = (mmc.getImageWidth() - width) / 2
    y = (mmc.getImageHeight() - height) / 2
    mmc.setROI(x, y, width, height)


def CV_FOURCC(c1, c2, c3, c4):
    """Missed in cv2."""
    return (c1 & 255) + ((c2 & 255) << 8) + ((c3 & 255) << 16) + ((c4 & 255) << 24)


def main():
    """Looping in function should be faster then in global scope."""
    mmc = MMCorePy.CMMCore()
    mmc.enableStderrLog(False)
    mmc.enableDebugLog(False)
    mmc.setCircularBufferMemoryFootprint(1500)
    mmc.loadDevice(*DEVICE)
    mmc.initializeDevice(DEVICE[0])
    mmc.setCameraDevice(DEVICE[0])
    mmc.setProperty(DEVICE[0], 'PixelType', '32bitRGB')

    cv2.namedWindow('MM controls')
    cv2.namedWindow('Video')
    if mmc.hasProperty(DEVICE[0], 'Gain'):
        cv2.createTrackbar(
            'Gain', 'MM controls',
            int(float(mmc.getProperty(DEVICE[0], 'Gain'))),
            int(mmc.getPropertyUpperLimit(DEVICE[0], 'Gain')),
            lambda value: mmc.setProperty(DEVICE[0], 'Gain', value))
    if mmc.hasProperty(DEVICE[0], 'Exposure'):
        cv2.createTrackbar(
            'Exposure', 'MM controls',
            int(float(mmc.getProperty(DEVICE[0], 'Exposure'))),
            100,  # int(mmc.getPropertyUpperLimit(DEVICE[0], 'Exposure')),
            lambda value: mmc.setProperty(DEVICE[0], 'Exposure', int(value)))
    # set_mmc_resolution(mmc, 1280, 1024)
    # set_mmc_resolution(mmc, 640, 480)
    # set_mmc_resolution(mmc, 320, 240)
    # codecArr = 'X264'
    codecArr = 'LAGS'  # Lagarith Lossless Codec
    fourcc = CV_FOURCC(
        ord(codecArr[0]),
        ord(codecArr[1]),
        ord(codecArr[2]),
        ord(codecArr[3]))
    out = cv2.VideoWriter(
        filename=OUT_VIDEO,
        fourcc=fourcc,  # '-1' Ask for an codec; '0' disables compressing.
        fps=20.0,
        frameSize=(mmc.getImageWidth(), mmc.getImageHeight()),
        isColor=True)
    assert(out.isOpened())
    mmc.startContinuousSequenceAcquisition(1)
    while True:
        if mmc.isBufferOverflowed():
            print('Buffer overflowed\a')  # Alert sound
            break
        start_time = time.time()  # FPS counter
        remcount = mmc.getRemainingImageCount()
        freecap = mmc.getBufferFreeCapacity()
        totalcap = mmc.getBufferTotalCapacity()
        print('%d frames, %d / %d = %.2f %%') % (remcount, freecap, totalcap, 100. * freecap / float(totalcap))
        print(mmc.getImageBufferSize())

        if remcount > 0:
            rgb32 = mmc.popNextImage()
            # rgb32 = mmc.getLastImage()
            bgr = rgb32.view(dtype=np.uint8).reshape(
                rgb32.shape[0], rgb32.shape[1], 4)[..., :3]
            cv2.imshow('Video', bgr)
            out.write(bgr)
        else:
            print('No frame')
        if cv2.waitKey(3) >= 0:
            break
        end_time = time.time()
        if end_time != start_time:
            # Prevent division by zero
            print('Cycle per second: %f') % (1. / (time.time() - start_time))

    # Take rest images from circular buffer.
    mmc.stopSequenceAcquisition()
    remcount = mmc.getRemainingImageCount()
    print('Remaining images in buffer: %d') % remcount
    for fn in xrange(remcount):
        rgb32 = mmc.popNextImage()
        bgr = rgb32.view(dtype=np.uint8).reshape(
            rgb32.shape[0], rgb32.shape[1], 4)[..., :3]
        print('Dump from buffer: %d') % (remcount - fn)
        out.write(bgr)

    out.release()
    mmc.reset()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
