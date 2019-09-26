#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 2014-05-16
@author: Eugene Dvoretsky

Put image to texture and show it with OpenGL.

TODO:
* Pixel buffer
* Correct image rotation
"""

import sys
import time
import numpy as np
from PySide import QtCore
from PySide import QtGui
from PySide import QtOpenGL
from OpenGL.GL import *
from OpenGL import ERROR_ON_COPY

ERROR_ON_COPY = True  # Prevent array copy or casting
# http://pyopengl.sourceforge.net/documentation/opengl_diffs.html

import MMCorePy

DEVICE = ['Camera', 'DemoCamera', 'DCam']
# DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
# DEVICE = ['Camera', "BaumerOptronic", "BaumerOptronic"]


class GLFrame(QtOpenGL.QGLWidget):
    """Video output widget.
    """
    def __init__(self, width, height):
        super(GLFrame, self).__init__()
        self._tex_width, self._tex_height = width, height
        self._tex_data = None
    
    def initializeGL(self):
        print('initializeGL')
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        # Установим параметры "оборачивания" текстуры
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        # Установим параметры фильтрации текстуры - линейная фильтрация
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # Prepare an empty texture.
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB,
            self._tex_width, self._tex_height,
            0, GL_RGB, GL_UNSIGNED_BYTE, self._tex_data)
        # glDeleteTextures(1, texture_id)

    def paintGL(self):
        # print('paintGL')
        # Place new texture data
        # Prevent segfault: glTexSubImage would not accept None.
        if self._tex_data is not None:
            glTexSubImage2D(
                GL_TEXTURE_2D, 0, 0, 0,
                self._tex_width, self._tex_height,
                GL_RGB, GL_UNSIGNED_BYTE, self._tex_data)

        glClearColor(0.4, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 1); glVertex3f(1, -1, -1)
        glTexCoord2f(1, 0); glVertex3f(1, 1, -1)
        glTexCoord2f(0, 0); glVertex3f(-1, 1, -1)
        glEnd()
        # glDisable(GL_TEXTURE_2D)

    def resizeGL(self, width, height):
        print('resizeGL')
        self.view_width, self.view_height = width, height
        glViewport(0, 0, self.view_width, self.view_height)

    def setData(self, array):
        """Pass an texture with same shape.
        """
        assert((self._tex_height, self._tex_width) == array.shape[:2])
        self._tex_data = array
        self.updateGL()


class VideoProcessor(QtCore.QThread):
    """Get frames."""
    def __init__(self, mmcamera):
        super(VideoProcessor, self).__init__()
        self.mmcamera = mmcamera
        self.running = True
        self.rgb32 = None
        self.rgb = None
        
    def run(self):
        self.mmcamera.snapImage()  # Avoid Baumer bug
        self.mmcamera.startContinuousSequenceAcquisition(1)
        
        start_time = time.time()
        while self.running is True:
            if self.mmcamera.getRemainingImageCount() > 0:
                start_time = time.time()
                # self.rgb32 = mmcamera.popNextImage()
                self.rgb32 = self.mmcamera.getLastImage()
                self.rgb = self.rgb32.view(dtype=np.uint8).reshape(
                    self.rgb32.shape[0], self.rgb32.shape[1], 4)[..., 2:: -1]
                self.emit(QtCore.SIGNAL('NewFrame()'))
                print('GET frame')
            else:
                print('No frame')
            time.sleep(0.020)
            print('FPS: %f') % (1. / (time.time() - start_time))

        self.mmcamera.stopSequenceAcquisition()
        self.mmcamera.reset()
        print('Video acquisition terminated.')
        # self.emit(QtCore.SIGNAL('CamReleased'))  # taskDone() may be better
    
    def control(self, trigger):
        if trigger is True:
            self.running = True
            self.start()
        if trigger is False:
            self.running = False
            print('Terminated')


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        mmc = MMCorePy.CMMCore()
        mmc.enableDebugLog(False)
        mmc.enableStderrLog(False)
        # mmc.setCircularBufferMemoryFootprint(100)
        mmc.loadDevice(*DEVICE)
        mmc.initializeDevice(DEVICE[0])
        mmc.setCameraDevice(DEVICE[0])
        mmc.setProperty(DEVICE[0], 'PixelType', '32bitRGB')
        # mmc.setROI(0, 0, 640, 480)

        self.VProcessor = VideoProcessor(mmc)
        self.VProcessor.start()
        self.setGeometry(100, 100, mmc.getImageWidth(), mmc.getImageHeight())
        self.widget = GLFrame(mmc.getImageWidth(), mmc.getImageHeight())
        self.setCentralWidget(self.widget)

        self.connect(self.VProcessor, QtCore.SIGNAL('NewFrame()'), self.redraw_any)

    def redraw_any(self):
        self.widget.setData(self.VProcessor.rgb)
        print('Drawing')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
