#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 2014-05-16
@author: Eugene Dvoretsky

Attempt to understand CallBack mechanism.

registerCallback(MMEventCallback cb)
Register a callback (listener class). MMCore will send notifications on
internal events using this interface
"""

import MMCorePy


class PyMMEventCallBack(MMCorePy.MMEventCallback):
    """Asynchronous events handlers.
    https://github.com/mdcurtis/micromanager-upstream/blob/master/MMCore/CoreCallback.cpp

    Callback object for MMCore device interface. Encapsulates
    (bottom) internal API for calls going from devices to the
    core.
    """
    @classmethod
    def onPropertiesChanged():
        print("Hello, Dolly")

    # def onPropertyChanged(self, name, propName, propValue):
    #     """Device signals that a specific property changed and reports the new value.
    #     """
    #     print('onPropertyChanged')  #, name, propName, propValue)

    # def onConfigGroupChanged(self, *args):
    #     """Callback indicating that a configuration group has changed.
    #     """
    #     pass

    # def onPixelSizeChanged(self, *args):
    #     """Callback indicating that Pixel Size has changed.
    #     """
    #     pass

    # def onStagePositionChanged(self, *args):
    #     """Handler for Stage position update.
    #     """
    #     pass

    # def onStagePositionChangedRelative(self, *args):
    #     """
    #     """
    #     pass

    # def onXYStagePositionChanged(self, *args):
    #     """Handler for XYStage position update.
    #     """
    #     pass

    # def onXYStagePositionChangedRelative(self, *args):
    #     """
    #     """
    #     pass

    # def onExposureChanged(self, name, newExposure):
    #     """Handler for exposure update.
    #     """
    #     print(name, newExposure)

    ## NOT IMPLEMENTED IN MMCorePy.py
    # def AcqFinished(self, *args):
    #     """Close the shutter if we are in auto mode.

    #     Don't wait for the shutter, because we typically call waitForDevice from
    #     a sequence thread and can cause a deadlock of shutter and camera
    #     are in the same module.
    #     """
    #     pass

    # def OnFinished(self, *args):
    #     """Handler for the operation finished event from the device.
    #     It looks like this handler does nothing
    #     """
    #     pass


if __name__ == '__main__':
    DEVICE = ['Camera', 'DemoCamera', 'DCam']
    # DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
    # DEVICE = ['Camera', 'BaumerOptronic', 'BaumerOptronic']
    mmc = MMCorePy.CMMCore()
    callback = PyMMEventCallBack()
    mmc.registerCallback(callback)
    # mmc.enableStderrLog(True)
    # mmc.enableDebugLog(True)
    mmc.loadDevice(*DEVICE)
    # mmc.initializeDevice(DEVICE[0])
    mmc.initializeAllDevices()
    mmc.setCameraDevice(DEVICE[0])
    mmc.setProperty('Camera', 'Exposure', '35.0')
    mmc.setProperty('Camera', 'Exposure', '48')
    mmc.setProperty('Camera', 'Binning', '2')
    # print('Change scanmode')
    mmc.setProperty('Camera', "ScanMode", "1")
    mmc.setProperty('Camera', "BitDepth", "10")
    print('End')
