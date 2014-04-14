#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 19 Jan. 2014.
@author: Eugene Dvoretsky

Live video acquisition with Micro-Manager adapter and opencv.
"""

import numpy as np
import cv2
import MMCorePy

DEVICE = ['Camera', 'DemoCamera', 'DCam']
# DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = ['Camera', "BaumerOptronic", "BaumerOptronic"]


if __name__ == '__main__':
    mmc = MMCorePy.CMMCore()
    mmc.enableStderrLog(False)
    mmc.enableDebugLog(False)
    # mmc.setCircularBufferMemoryFootprint(100)
    mmc.loadDevice(*DEVICE)
    mmc.initializeDevice(DEVICE[0])
    mmc.setCameraDevice(DEVICE[0])
    mmc.setProperty(DEVICE[0], 'PixelType', '32bitRGB')

    cv2.namedWindow('Video')
    mmc.startContinuousSequenceAcquisition(1)
    while True:
        rgb32 = mmc.getLastImage()
        if mmc.getRemainingImageCount() > 0:
            # rgb32 = mmc.popNextImage()
            rgb32 = mmc.getLastImage()
            # Efficient conversion without data copying.
            bgr = rgb32.view(dtype=np.uint8).reshape(
                rgb32.shape[0], rgb32.shape[1], 4)[..., :3]
            cv2.imshow('Video', bgr)
        else:
            print('No frame')
        if cv2.waitKey(20) >= 0:
            break
    cv2.destroyAllWindows()
    mmc.stopSequenceAcquisition()
    mmc.reset()
