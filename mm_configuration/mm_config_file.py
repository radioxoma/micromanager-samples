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

# devlabel = 'Camera'

# DEVICE = [devlabel, 'DemoCamera', 'DCam']
# DEVICE = [devlabel, 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = [devlabel, "BaumerOptronic", "BaumerOptronic"]

mmc = MMCorePy.CMMCore()
# mmc.enableStderrLog(False)
# mmc.enableDebugLog(False)
# mmc.loadDevice(*DEVICE)
# mmc.initializeAllDevices()
# mmc.setCameraDevice(devlabel)


# GROUP CONTAINS CONFIGS (PRESETS).


# Creates an empty configuration group. Not really needed.
# mmc.defineConfigGroup("groupName")

# Defines a configuration. Without error creates config.
# mmc.defineConfig('groupName', 'configName')

# Defines a single configuration entry. Without error creates config.
# mmc.defineConfig('groupName', 'configName', devlabel, 'Exposure', '30')

mmc.loadSystemConfiguration("MMConfig_dcam.cfg")


# INSPECT CONFIGURATION

print('\ngetAvailableConfigGroups')
for groupName in mmc.getAvailableConfigGroups():
    print('%s\t%s') % (groupName, mmc.getAvailableConfigs(groupName))
    # if mmc.isGroupDefined('groupName'):
    #     print('getConfigGroupState', cat(mmc.getConfigGroupState('groupName')))
    #     if mmc.isConfigDefined('groupName', 'configName'):
    for configName in mmc.getAvailableConfigs(groupName):
        print('CD: %s\t%s') % (configName, mmc.getConfigData(groupName, configName).getVerbose())
        print('CS: %s\t%s') % (configName, mmc.getConfigState(groupName, configName).getVerbose())


# CONTROL
print('')

# print('getProperty', mmc.getProperty(devlabel, 'Exposure'))
# Apply config to group
# mmc.setConfig('groupName', 'configName')
# print('getProperty', mmc.getProperty(devlabel, 'Exposure'))
# Smt weird
# print('getCurrentConfig', mmc.getCurrentConfig('groupName'))


# ***

# Create an simple config:
# mmc.definePixelSizeConfig('Res100x')
# ConfigPixelSize,Res40x,Objective,Label,Nikon 40X Plan Flueor ELWD
# Or verbose one:
# PixelSize_um,Res40x,0.25
# Set pixel size for it.

print('\ngetAvailablePixelSizeConfigs')
for confname in mmc.getAvailablePixelSizeConfigs():
    print("%s\t%.3f um/px") % (confname, mmc.getPixelSizeUmByID(confname))
    pxsize_conf = mmc.getPixelSizeConfigData(confname)
    # print('getPixelSizeConfigData %s') % pxsize_conf.getVerbose()
    if pxsize_conf.isPropertyIncluded('DObjective', 'Label'):
        prop = pxsize_conf.getSetting('DObjective', 'Label')
        print(
            prop.getDeviceLabel(),
            prop.getPropertyName(),
            prop.getReadOnly(),
            prop.getPropertyValue())

# Can't use without real devise
print('\ngetMagnificationFactor: %s') % mmc.getMagnificationFactor()
print('getCurrentPixelSizeConfig: %s') % mmc.getCurrentPixelSizeConfig()
# mmc.setPixelSizeConfig('100x')
print('getPixelSizeUm: %s') % mmc.getPixelSizeUm()  # (based on getMagnificationFactor)
# print('getSystemState %s' % '\n'.join(mmc.getSystemState().getVerbose().split('<br>')))

# mmc.saveSystemConfiguration("MMConfig_genSysConfig.cfg")
# mmc.saveSystemState("MMConfig_genSystemState.cfg")
print('getAvailablePropertyBlocks:', mmc.getAvailablePropertyBlocks())
