# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alert_unit.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AlertUnit(object):
    def setupUi(self, AlertUnit):
        AlertUnit.setObjectName("AlertUnit")
        AlertUnit.resize(500, 176)
        AlertUnit.setMinimumSize(QtCore.QSize(500, 150))
        self.verticalLayout = QtWidgets.QVBoxLayout(AlertUnit)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(AlertUnit)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.eventNumQLabel = QtWidgets.QLabel(AlertUnit)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.eventNumQLabel.setFont(font)
        self.eventNumQLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.eventNumQLabel.setObjectName("eventNumQLabel")
        self.verticalLayout.addWidget(self.eventNumQLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(AlertUnit)
        QtCore.QMetaObject.connectSlotsByName(AlertUnit)

    def retranslateUi(self, AlertUnit):
        _translate = QtCore.QCoreApplication.translate
        AlertUnit.setWindowTitle(_translate("AlertUnit", "Кнопка Жизни"))
        self.label.setText(_translate("AlertUnit", "Количество срабатываний:"))
        self.eventNumQLabel.setText(_translate("AlertUnit", "0"))
