#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 23 March 2014.
@author: Eugene Dvoretsky

Live video acquisition with Micro-Manager adapter and opencv.
Another example with exposure and gain control.
"""

import numpy as np
import cv2
import MMCorePy

WIDTH, HEIGHT = 320, 240
DEVICE = ['Camera', 'DemoCamera', 'DCam']
# DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = ['Camera', "BaumerOptronic", "BaumerOptronic"]


def set_mmc_resolution(mmc, width, height):
    """Select rectangular ROI in center of the frame.
    """
    x = (mmc.getImageWidth() - width) / 2
    y = (mmc.getImageHeight() - height) / 2
    mmc.setROI(x, y, width, height)


def main():
    """Looping in function should be faster then in global scope.
    """
    mmc = MMCorePy.CMMCore()
    mmc.enableStderrLog(False)
    mmc.enableDebugLog(False)
    # mmc.setCircularBufferMemoryFootprint(100)
    mmc.loadDevice(*DEVICE)
    mmc.initializeDevice(DEVICE[0])
    mmc.setCameraDevice(DEVICE[0])
    mmc.setProperty(DEVICE[0], 'PixelType', '32bitRGB')

    cv2.namedWindow('MM controls')
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

    set_mmc_resolution(mmc, WIDTH, HEIGHT)
    mmc.snapImage()  # Baumer workaround
    cv2.namedWindow('Video')
    mmc.startContinuousSequenceAcquisition(1)
    while True:
        remcount = mmc.getRemainingImageCount()
        print('Images in circular buffer: %s') % remcount
        if remcount > 0:
            # rgb32 = mmc.popNextImage()
            rgb32 = mmc.getLastImage()
            bgr = rgb32.view(dtype=np.uint8).reshape(
                rgb32.shape[0], rgb32.shape[1], 4)[..., :3]
            cv2.imshow('Video', bgr)
        else:
            print('No frame')
        if cv2.waitKey(5) >= 0:
            break
    cv2.destroyAllWindows()
    mmc.stopSequenceAcquisition()
    mmc.reset()


if __name__ == '__main__':
    main()
