#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 08 April 2017.
@author: Eugene Dvoretsky

Take a single photo with camera and show it.
"""

import MMCorePy

devlabel = "Camera"
DEVICE = [devlabel, "GPhoto", "GPhoto"]

mmc = MMCorePy.CMMCore()
mmc.loadDevice(*DEVICE)
mmc.initializeDevice(devlabel)
mmc.setCameraDevice(devlabel)

mmc.snapImage()
img = mmc.getImage()

import matplotlib.pyplot as plt
plt.imshow(img, cmap='gray')
plt.show()  # And window with an image will appear
