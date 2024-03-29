from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot
import alert_unit


class Widget(QtWidgets.QWidget, alert_unit.Ui_AlertUnit):
    alert_number = QtCore.pyqtSignal(int)

    def __init__(self):
        super(Widget, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icon_alert.png'))

    def label_value_change(self, i):
        self.eventNumQLabel.setText(f"{i:d}")
        pass
