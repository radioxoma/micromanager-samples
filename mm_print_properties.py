#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 19 Jan. 2014.
@author: Eugene Dvoretsky

Print available camera properties with Micromanager interface.
"""

import MMCorePy
from time import sleep

devlabel = 'Camera'

DEVICE = [devlabel, 'DemoCamera', 'DCam']
# DEVICE = [devlabel, 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = [devlabel, "BaumerOptronic", "BaumerOptronic"]

mmc = MMCorePy.CMMCore()
mmc.loadDevice(*DEVICE)
mmc.initializeDevice(devlabel)
# mmc.initializeAllDevices()
mmc.setCameraDevice(devlabel)

sleep(1)  # I don't want synchronize threads.

print('\n\t* Common information *')
print("User '%s' on host '%s'") % (mmc.getUserId(), mmc.getHostName())
print('getVersionInfo: %s') % mmc.getVersionInfo()
print('getAPIVersionInfo: %s') % mmc.getAPIVersionInfo()
print('getDeviceType: %s') % mmc.getDeviceType(devlabel)
print('getPixelSizeUm: %s') % mmc.getPixelSizeUm()

#-------------------------------------
print('\n\t* Getting property list *')
#-------------------------------------
proptyple = mmc.getDevicePropertyNames(devlabel)
for prop in proptyple:
    print("%s '%s' RO: %s" % (
        prop,
        mmc.getProperty(devlabel, prop),
        mmc.isPropertyReadOnly(devlabel, prop)))

    if mmc.hasPropertyLimits(devlabel, prop):
        print('hasPropertyLimits: %s to %s') % (
            mmc.getPropertyLowerLimit(devlabel, prop),
            mmc.getPropertyUpperLimit(devlabel, prop))
    else:
        print("VALUES: " + ', '.join(mmc.getAllowedPropertyValues(devlabel, prop)))

    if mmc.isPropertySequenceable(devlabel, prop):
        print('PropertySequenceable')
    if mmc.isPropertyPreInit(devlabel, prop):
        print('PropertyPreInit')

    print('')


#-----------------------------------
print('\t* Frame parameters *')
#-----------------------------------

# Image buffer size.
print('Width %d, Height %d') % (mmc.getImageWidth(), mmc.getImageHeight())
print('getROI', mmc.getROI())

# 32 MByte by default?
# GetImageBufferSize() = img_.Width() * img_.Height() * GetImageBytesPerPixel()
print('getBytesPerPixel: %s') % mmc.getBytesPerPixel()
print('getImageBitDepth: %s') % mmc.getImageBitDepth()


#-----------------------------------
print('\n\t* Test acquisition *')
#-----------------------------------
mmc.startContinuousSequenceAcquisition(1)
# Видимо буфер инициализируется только при захвате.
print('getBufferTotalCapacity: %s') % mmc.getBufferTotalCapacity()
print('getBufferFreeCapacity: %s') % mmc.getBufferFreeCapacity()

print('getExposure %s') % mmc.getExposure()
mmc.setProperty(devlabel, 'Exposure', 15)
print('getExposure %s') % mmc.getExposure()


#-----------------------------------
print('\n\t* Frame metadata *')
#-----------------------------------
md = MMCorePy.Metadata()
img = mmc.getLastImageMD(0, 0, md)
# print(img.shape)
print(md.Dump())


#-------------------------
print('\n\t* Reset all *')
#-------------------------
mmc.stopSequenceAcquisition()
mmc.reset()
