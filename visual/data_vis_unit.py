# Form implementation generated from reading ui file 'data_vis_unit.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_dataVisUnitOName(object):
    def setupUi(self, dataVisUnitOName):
        dataVisUnitOName.setObjectName("dataVisUnitOName")
        dataVisUnitOName.resize(1153, 295)
        dataVisUnitOName.setMinimumSize(QtCore.QSize(450, 150))
        self.verticalLayout = QtWidgets.QVBoxLayout(dataVisUnitOName)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dataGraphGView = PlotWidget(parent=dataVisUnitOName)
        self.dataGraphGView.setMinimumSize(QtCore.QSize(450, 100))
        self.dataGraphGView.setObjectName("dataGraphGView")
        self.verticalLayout.addWidget(self.dataGraphGView)

        self.retranslateUi(dataVisUnitOName)
        QtCore.QMetaObject.connectSlotsByName(dataVisUnitOName)

    def retranslateUi(self, dataVisUnitOName):
        _translate = QtCore.QCoreApplication.translate
        dataVisUnitOName.setWindowTitle(_translate("dataVisUnitOName", "data_vis_unit"))
from pyqtgraph import PlotWidget
