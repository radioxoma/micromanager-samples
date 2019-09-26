#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 2014-05-24
@author: Eugene Dvoretsky

MMCore pixel size
"""

import MMCorePy

def cat(config):
    """Concatenate config."""
    return '\n'.join(config.getVerbose().split('<br>'))

devlabel = 'Camera'

DEVICE = [devlabel, 'DemoCamera', 'DCam']
# DEVICE = [devlabel, 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = [devlabel, "BaumerOptronic", "BaumerOptronic"]

mmc = MMCorePy.CMMCore()
# mmc.enableStderrLog(False)
# mmc.enableDebugLog(False)
mmc.loadDevice(*DEVICE)
mmc.initializeAllDevices()
mmc.setCameraDevice(devlabel)


# GROUP CONTAINS CONFIGS (PRESETS).


# Creates an empty configuration group. Not really needed.
# mmc.defineConfigGroup("groupName")

# Defines a configuration. Without error creates config.
# mmc.defineConfig('groupName', 'configName')

# Defines a single configuration entry. Without error creates config.
mmc.defineConfig('groupName', 'configName', devlabel, 'Exposure', '30')
# mmc.loadSystemConfiguration("MMConfig.cfg")


# INSPECT CONFIGURATION

print('getAvailableConfigGroups', mmc.getAvailableConfigGroups())

if mmc.isGroupDefined('groupName'):
    print('getAvailableConfigs', mmc.getAvailableConfigs('groupName'))
    print('getConfigGroupState', cat(mmc.getConfigGroupState('groupName')))
    if mmc.isConfigDefined('groupName', 'configName'):
        print('getConfigState', cat(mmc.getConfigState('groupName', 'configName')))


# CONTROL
print('')

print('getProperty', mmc.getProperty(devlabel, 'Exposure'))
# Apply config to group
mmc.setConfig('groupName', 'configName')
print('getProperty', mmc.getProperty(devlabel, 'Exposure'))
# Smt weird
# print('getCurrentConfig', mmc.getCurrentConfig('groupName'))


# ***

# mmc.setPixelSizeUm(const char *resolutionID, double pixSize)
# mmc.setPixelSizeUm('resolutionID', 0.1)
# mmc.setPixelSizeConfig(const char *resolutionID)

print('')
print('getAvailablePixelSizeConfigs', mmc.getAvailablePixelSizeConfigs())
print('getPixelSizeUm', mmc.getPixelSizeUm())  # (based on getMagnificationFactor)

# print('getSystemState %s' % '\n'.join(mmc.getSystemState().getVerbose().split('<br>')))

# Property,Core,Initialize,0
mmc.saveSystemConfiguration("MMConfig.cfg")
