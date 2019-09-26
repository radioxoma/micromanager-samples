#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on 2014-07-03
@author: Eugene Dvoretsky

Qt-based Micromanager property browser. Taken from my
[Immunopy](https://github.com/radioxoma/immunopy) project.
"""

from PySide import QtCore
from PySide import QtGui


class MicromanagerPropertyModel(QtCore.QAbstractTableModel):
    """Micromanager property model.

    May be should use callback if CMMCore property has accidentally changes?
    Can't use CMMCore callbacks cause Micromanager insufficient implementation.
    """
    def __init__(self, mmcore, deviceLabel):
        super(MicromanagerPropertyModel, self).__init__()
        self.mmc = mmcore
        self.dlabel = deviceLabel
        self.pnames = list(self.mmc.getDevicePropertyNames(self.dlabel))
        self.__header = ('Property', 'Value', 'Type')

    def rowCount(self, index, parent=QtCore.QModelIndex()):
        """Returns the number of rows under the given parent.

        When the parent is valid it means that rowCount is returning
        the number of children of parent.
        """
        return len(self.pnames)

    def columnCount(self, index, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred
        to by the index.
        """
        if not index.isValid() or index.row() >= len(self.pnames):
            return None
        propname = self.pnames[index.row()]
        if index.column() == 0 and role == QtCore.Qt.DisplayRole:
            return propname
        proptype = self.getPtype(propname)
        if index.column() == 2 and role == QtCore.Qt.DisplayRole:
            return unicode(proptype)
        if index.column() == 1 and \
                (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
            # Casting MM property string to appropriate datatype
            return proptype(
                self.mmc.getProperty(self.dlabel, propname).replace(',', '.'))
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """Sets the role data for the item at index to value.
        """
        if index.isValid() and role == QtCore.Qt.EditRole:
            print(value, type(value))
            self.mmc.setProperty(
                self.dlabel, self.pnames[index.row()], str(value))
            print('getProp', self.mmc.getProperty(
                self.dlabel, self.pnames[index.row()]))
            self.dataChanged.emit(index, index)
            return True  # If core accept data
        else:
            return False

    def flags(self, index):
        """Returns the item flags for the given index.
        """
        if index.isValid():
            idx = index.row()
            if self.mmc.isPropertyReadOnly(self.dlabel, self.pnames[idx]) or \
                    self.mmc.isPropertyPreInit(self.dlabel, self.pnames[idx]):
                return QtCore.Qt.NoItemFlags
            if index.column() == 0 or index.column() == 2:
                return QtCore.Qt.ItemIsEnabled
            elif index.column() == 1:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Returns the data for the given role and section in the header with
        the specified orientation.
        """
        if role == QtCore.Qt.DisplayRole:
            self.__header
            if orientation == QtCore.Qt.Horizontal:
                return self.__header[section]
            else:
                return '%.2d' % (section + 1)
        else:
            return None

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        if column == 0:
            if order == QtCore.Qt.AscendingOrder:
                self.pnames.sort()
            else:
                self.pnames.sort(reverse=True)
        print('Sorting', column, order)

    def getPtype(self, propname):
        """Replacement for C-style enum.
        """
        proptype = self.mmc.getPropertyType(self.dlabel, propname)
        types = (None, str, float, int)
        return types[proptype]


class MicromanagerPropertyDelegate(QtGui.QStyledItemDelegate):
    """Micromanager advanced editor.

    I don't use a factory, because it's necessary to adjust specific
    property-dependent widget parameters.
    """
    def __init__(self, deviceLabel):
        super(MicromanagerPropertyDelegate, self).__init__()
        self.dlabel = deviceLabel

    def createEditor(self, parent, option, index):
        """Returns an widget with specific adjustments.

        This method aware about Micromanager and property model restrictions:
        e.g. range limit and allowed values.

        readonly -> str
        preinit -> str
        mutable
            hasPropertyLimits
                low
                up
                type {integer, double}
            state {var0, var1, var2} -> str
        """
        if not index.isValid():
            return None
        self.mmc = index.model().mmc
        # Get appropriate property name from DisplayRole data.
        # propname = index.model().data(index.model() \
        #     .createIndex(index.row(), 0))
        propname = index.model().pnames[index.row()]
        value = index.model().data(index, QtCore.Qt.EditRole)
        proptype = type(value)
        if self.mmc.hasPropertyLimits(self.dlabel, propname):
            if isinstance(value, int):
                editor = QtGui.QSpinBox(parent=parent)
            elif isinstance(value, float):
                editor = QtGui.QDoubleSpinBox(parent=parent)
            editor.setMaximum(proptype(
                self.mmc.getPropertyUpperLimit(self.dlabel, propname)))
            editor.setMinimum(proptype(
                self.mmc.getPropertyLowerLimit(self.dlabel, propname)))
        else:
            editor = QtGui.QComboBox(parent=parent)
            editor.addItems(
                self.mmc.getAllowedPropertyValues(self.dlabel, propname))
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor, index):
        """Set data in widget-specific way.
        """
        value = index.model().data(index, QtCore.Qt.EditRole)
        if isinstance(editor, QtGui.QLineEdit):
            editor.setText(value)
        elif isinstance(editor, QtGui.QComboBox):
            idx = editor.findText(unicode(value))
            editor.setCurrentIndex(idx)
        else:
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        """Returns updated widget data to the model.
        """
        if isinstance(editor, QtGui.QLineEdit):
            value = editor.text()
        elif isinstance(editor, QtGui.QComboBox):
            value = editor.currentText()
        else:
            editor.interpretText()
            value = editor.value()
        model.setData(index, value, QtCore.Qt.EditRole)


class MicromanagerPropertyBrowser(QtGui.QDialog):
    """Allows discover and change Micromanager device properties.
    """
    def __init__(self, model, parent=None):
        super(MicromanagerPropertyBrowser, self).__init__()
        self.parent = parent
        self.model = model
        self.setMinimumSize(450, 600)
        self.setWindowTitle("%s property browser" % self.model.dlabel)
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.view = QtGui.QTableView()
        self.view.setSortingEnabled(True)
        self.view.setWordWrap(False)
        self.view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.view.setModel(self.model)
        self.delegate = MicromanagerPropertyDelegate(
            deviceLabel=self.model.dlabel)
        self.view.setItemDelegate(self.delegate)
        self.vbox.addWidget(self.view)
        self.showPropertyBrowserAction = QtGui.QAction(self)
        self.showPropertyBrowserAction.setText("&Configure device...")
        self.showPropertyBrowserAction.triggered.connect(self.show)


if __name__ == '__main__':
    import sys
    import MMCorePy
    DEVICE = ['Camera', 'DemoCamera', 'DCam']
    # DEVICE = ['Camera', 'OpenCVgrabber', 'OpenCVgrabber']
    # DEVICE = ['Camera', 'BaumerOptronic', 'BaumerOptronic']
    MMC = MMCorePy.CMMCore()
    MCCallback = MMCorePy.MMEventCallback()
    MMC.registerCallback(MCCallback)
    MMC.loadDevice(*DEVICE)
    MMC.initializeDevice(DEVICE[0])
    MMC.setCameraDevice(DEVICE[0])

    app = QtGui.QApplication(sys.argv)
    model = MicromanagerPropertyModel(MMC, MMC.getCameraDevice())
    window = MicromanagerPropertyBrowser(model)
    window.show()
    app.exec_()
