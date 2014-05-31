#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 19 Jan. 2014.
@author: Eugene Dvoretsky

Discovery MMCore properties.
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

print(
    """
    -----------------------------------------------------------------------
                            Common information
    -----------------------------------------------------------------------
    """)

print("User '%s' on host '%s'") % (mmc.getUserId(), mmc.getHostName())
print('getVersionInfo: %s') % mmc.getVersionInfo()
print('getAPIVersionInfo: %s') % mmc.getAPIVersionInfo()
print('getDeviceType: %s') % mmc.getDeviceType(devlabel)
print('getDeviceDescription: %s') % mmc.getDeviceDescription(devlabel)
print('getDeviceLibrary: %s') % mmc.getDeviceLibrary(devlabel)
print('getPixelSizeUm: %s') % mmc.getPixelSizeUm()

# Too verbose output.

print(
    """
    -----------------------------------------------------------------------
                            Libraries & devices
    -----------------------------------------------------------------------
    """)

print('getDeviceAdapterSearchPaths: %s') % ''.join(mmc.getDeviceAdapterSearchPaths())
for libname in mmc.getDeviceAdapterNames():
    try:
        # Get available devices from the specified device library.
        print("'%s':\t%s") % (libname, mmc.getAvailableDevices(libname))
    except MMCorePy.CMMError:
        print("'%s':\tWon't work") % libname

    # try:
    #     # Available if device is loaded.
    #     for dev in mmc.getAvailableDevices(libname):
    #         print('getDeviceDescription: %s', mmc.getDeviceDescription(dev))
    # except MMCorePy.CMMError:
    #     print('No DeviceDescription')

#-------------------------------------------------------------------------------

print(
    """
    -----------------------------------------------------------------------
                        Getting '%s' property list
    -----------------------------------------------------------------------
    """ % devlabel)


def get_prop_type(devlabel, prop):
    """Not implemented in MMCorePy.
    """
    t = mmc.getPropertyType(devlabel, prop)
    if t == 0:  # Undef probably
        return None
    elif t == 1:  # String
        return str
    elif t == 2:  # Float
        return float
    elif t == 3:  # Integer
        return int
    else:
        raise ValueError("Unexpected property type '%s'" % t)


def readFromCore(prop):
    info = "%s: '%s'" % (prop, mmc.getProperty(devlabel, prop))

    if mmc.isPropertyPreInit(devlabel, prop):
        print('\tPropertyPreInit')
    if mmc.isPropertySequenceable(devlabel, prop):
        print('\tPropertySequenceable')

    if mmc.hasPropertyLimits(devlabel, prop):
        low = mmc.getPropertyLowerLimit(devlabel, prop)
        up = mmc.getPropertyUpperLimit(devlabel, prop)
        prop_type = get_prop_type(devlabel, prop)
        if prop_type is float:
            info += " in range: %s - %s" % (low, up)
        elif prop_type is int:
            info += " in steps between %s and %s" % (low, up)
        else:
            raise ValueError("Unexpected property type '%s'" % prop_type)
    available_vals = ', '.join(mmc.getAllowedPropertyValues(devlabel, prop))
    if available_vals:
        info += " from {%s}" % available_vals
    print(info)

prop_ro = list()
prop_ed = list()
for prop in mmc.getDevicePropertyNames(devlabel):
    if mmc.isPropertyReadOnly(devlabel, prop):
        prop_ro.append(prop)
    else:
        prop_ed.append(prop)
prop_ed.sort(key=lambda prop: mmc.getPropertyType(devlabel, prop))

print(
    """
                        * Read-only properties *
    """)
for prop in prop_ro:
    readFromCore(prop)

print(
    """
                        * Mutable properties *
    """)
for prop in prop_ed:
    readFromCore(prop)


print(
    """
                        * Frame parameters *
    """)
# Image buffer size.
print('Width %d, Height %d') % (mmc.getImageWidth(), mmc.getImageHeight())
print('getROI [%s]') % ', '.join([str(k) for k in mmc.getROI()])

# 32 MByte by default?
# GetImageBufferSize() = img_.Width() * img_.Height() * GetImageBytesPerPixel()
print('getBytesPerPixel: %s') % mmc.getBytesPerPixel()
print('getImageBitDepth: %s') % mmc.getImageBitDepth()


print(
    """
                        * Acquisition test *
    """)

mmc.startContinuousSequenceAcquisition(1)
# Видимо буфер инициализируется только при захвате.
print('getBufferTotalCapacity: %s') % mmc.getBufferTotalCapacity()
print('getBufferFreeCapacity: %s') % mmc.getBufferFreeCapacity()

print('getExposure %s') % mmc.getExposure()
mmc.setProperty(devlabel, 'Exposure', 15)
print('getExposure %s') % mmc.getExposure()


print(
    """
                        * Frame metadata *
    """)
md = MMCorePy.Metadata()
img = mmc.getLastImageMD(0, 0, md)
# print(img.shape)
print(md.Dump())

print(
    """
                        * Reset all *
    """)
mmc.stopSequenceAcquisition()
mmc.reset()
