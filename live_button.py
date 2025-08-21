import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
import live_button_win
import time
import os
import mim
import mim_rs_485
from transaction_list import *
from threading import Thread, Lock, Event
from queue import Queue, Empty
from loguru import logger
import alert_win
import json
import re
from datetime import datetime, timedelta, timezone


class MainWindow(QtWidgets.QMainWindow, live_button_win.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле main_win.py
        #
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("Регистратор событий \"Кнопка жизни\"")

        #
        self.live_buttons_pattern = bytes.fromhex(" 77 00 00 00 00 00 00 33 ")
        self.live_buttons_event_num = 0

        # всплывающее окно
        self.alert_win = alert_win.Widget()

        # подключаемые модули
        self.mim = mim.MimRS485Device(alias="MIM", addr=0x00, serial_numbers=["A50285"], debug=True)
        self.logger = logger
        self.logger.add("logs\\Live_Buttons_log_{time}.log", rotation="1 hours")

        self.load_init_cfg()
        self.COMPortLEdit.setText(self.mim.port)
        self.SerialNumEntry.setText(self.mim.serial_numbers[-1])
        self.pollingIntervalDSBox.setValue(0.8)

        self.last_cursor = QtGui.QTextCursor.MoveOperation.Start

        # обработка кнопок
        self.COMPortOpenPButt.clicked.connect(self.open_by_port)
        self.SNPortOpenPButt.clicked.connect(self.open_by_sn)
        self.setDefaultPButt.clicked.connect(self.set_defaults)

        # чтение результата измерения
        self.pollingStartPButt.clicked.connect(self.polling_start)
        self.pollingStopPButt.clicked.connect(self.polling_stop)
        self.pollingTimer = QtCore.QTimer()
        self.pollingTimer.timeout.connect(self.polling_body)

        # вычитка сообщений в текстовый редактор
        self.logTimer = QtCore.QTimer()
        self.logTimer.timeout.connect(self.log_refresh)
        self.logTimer.start(200)

        # timeout
        self.timeoutTimer = QtCore.QTimer()
        self.timeoutTimer.timeout.connect(self.timeout)
        self.timeout_flag = False


        # потоки общения с прибором
        self.mim_queue = Queue(maxsize=128)
        self.log_queue = Queue(maxsize=256)
        self.trans_lock = Lock()
        self.polling_close_e = Event()
        self.t_polling = Thread(target=self.cylogramma,
                                args=(
                                    self.mim, self.mim_queue, self.log_queue, self.trans_lock,
                                    self.polling_close_e,
                                    self.logger),
                                daemon=True)
        self.t_polling.start()
        #

    # polling
    def polling_start(self):
        self.pollingStartPButt.setStyleSheet("background-color: " + "SpringGreen")
        interval = int(self.pollingIntervalDSBox.value()*1000)
        self.pollingTimer.start(interval)
        pass

    def polling_body(self):
        if self.mim.is_open:
            # item = MIM_RS485_MAP(alias="mfr_rx_polling", addr=0x0C, id=64, flag="data", data=None)
            item = MIM_RS485_MAP(alias="rx_polling", addr=0x0C, id=22, flag="data", data=None)
            self.mim_queue.put(item, block=False, timeout=None)
        pass

    def polling_stop(self):
        self.pollingStartPButt.setStyleSheet("background-color: " + "palette(Button)")
        self.pollingTimer.stop()
        pass

    def set_defaults(self):
        modules = [i for i in range(6)]
        for module in modules:
            if module == 5:
                item = MIM_RS485_MAP(alias="apply cfg", addr=0x0C, id=21, flag="cmd", data=bytes.fromhex("13 00 46 01 06 00 01 00 12 00 00 A1 BC 33 01 00 00 00 00 00 00 00 00 00 00 00 A8 61 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0A 07 00 00 00 00 00 00 00 12 00 00 A1 BC 33 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00 00 00 12 00 00 A1 BC 33 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00 00 00 34 00 00 A1 BC 33 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00"))
            if module == 4:
                item = MIM_RS485_MAP(alias="apply cfg", addr=0x0C, id=21, flag="cmd", data=bytes.fromhex("13 00 46 01 05 00 01 00 12 00 00 A1 BC 33 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00 00 00 12 00 00 A1 BC 33 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00 00 00 12 00 80 FD 9C 76 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00 00 00 12 00 80 FD 9C 76 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 0A 07 00 00 00 00 00"))
            else:
                item = MIM_RS485_MAP(alias="apply cfg", addr=0x0C, id=3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[module, 0]).form_packet())
            try:
                self.mim_queue.put(item, block=False, timeout=None)
            except Empty:
                pass
        pass

    # connection
    def open_by_port(self):
        port = self.COMPortLEdit.text()
        self.mim.port = port
        self.mim.open_port()
        pass

    def open_by_sn(self):
        sn = self.SerialNumEntry.text()
        self.mim.serial_numbers = [sn]
        self.mim.open_id()
        pass

    @staticmethod
    def cylogramma(mim, mim_queue: Queue, log_queue: Queue, lock: Lock, close_e: Event, logger: logger):
        #
        error_cnt = 0
        msg = None
        log_msg = ""
        #
        while True:
            time.sleep(0.1)  # для устойчивой работы потока
            #
            if not mim_queue.empty():
                try:
                    msg = mim_queue.get(block=False, timeout=None)
                except Empty:
                    msg = None
            else:
                msg = None
            #
            if msg:
                transaction_start = time.perf_counter()
                tx_frame = mim.request(addr=msg.addr, id=msg.id, mode=msg.flag, data=msg.data)
                log_msg = f"{mim.alias}: tx_data {len(tx_frame)} (id={msg.id}) {tx_frame.hex(' ').upper()}"
                logger.info(log_msg), log_queue.put(log_msg)
                #
                while mim.ready_to_transaction is False:
                    time.sleep(0.010)
                #
                rx_frame = mim.get_last_data()
                if rx_frame:
                    log_msg = f"{mim.alias}: rx_data {len(rx_frame)} (id={msg.id}) t={(time.perf_counter() - transaction_start):.3f} {(rx_frame.hex(' ').upper())} id <{mim.check_frame(fr=rx_frame)}>"
                    logger.info(log_msg), log_queue.put(log_msg)
                    pass
                else:
                    log_msg = f"{mim.alias}: rx_error t={(time.perf_counter() - transaction_start):.3f} rx_data (id={msg.id})"
                    logger.info(log_msg), log_queue.put(log_msg)
                    error_cnt += 1
            #
            if close_e.is_set():
                close_e.clear()
                log_msg = f"\t{mim.alias}: user termination"
                logger.info(log_msg), log_queue.put(log_msg)
                return

    def find_str(self, str_to_find):
        ret_val = False
        self.LogTEdit.moveCursor(self.last_cursor)
        self.LogTEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End, QtGui.QTextCursor.MoveMode.KeepAnchor)
        self.LogTEdit.setTextBackgroundColor(QtGui.QColor("palette(Base)"))
        self.LogTEdit.setTextColor(QtGui.QColor("palette(Text)"))
        self.LogTEdit.moveCursor(QtGui.QTextCursor.MoveOperation.Start)
        while self.LogTEdit.find(str_to_find):
            self.LogTEdit.setTextBackgroundColor(QtGui.QColor("palette(Text)"))
            self.LogTEdit.setTextColor(QtGui.QColor("palette(Base)"))
            ret_val = True
            pass
        self.LogTEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.last_cursor = QtGui.QTextCursor.MoveOperation.End
        return ret_val

    def log_refresh(self):
        while not self.log_queue.empty():
            try:
                text = self.log_queue.get()
                logger.info(f"Received text to log window: {text}")
                search_sos_result = self.get_sos_from_transport_frame(text)
                if search_sos_result:
                    start= text.find(search_sos_result[-1])
                    text = text[:start] + "<font color='#1E4D31' size = 5>" + text[start:start+len(search_sos_result[-1])] + "</font>" + text[start+len(search_sos_result[-1]):]
                #
                self.LogTEdit.append(text)
                #
                
                #
                if search_sos_result:
                    time_b = bytes.fromhex(search_sos_result[-1])[2:]
                    time_s = int.from_bytes(time_b, byteorder='little')
                    datetime_from_seconds = datetime(1970, 1, 1, hour=7) + timedelta(seconds=time_s)
                    #
                    if self.timeout_flag is False:
                        self.timeoutTimer.singleShot(2000, self.timeout)
                        self.timeout_flag = True
                        self.live_buttons_event_num += 1
                        if self.viewAlertChBox.isChecked:
                            self.alert_win.show()
                            self.alert_win.label_value_change(self.live_buttons_event_num)
                            self.alert_win.label2_value_change(f"{datetime_from_seconds}")
                #
            except Empty:
                pass
        pass
    
    def get_sos_from_transport_frame(self, text):
        frame = re.compile(r"F0 00 0C [0-9A-F]{2} 00 3B (([0-9A-F]{2} ){0,59})(?P<sos>11 10 ([0-9A-F\s]{3}){4})(([0-9A-F]{2} ){0,59})([0-9A-F]{2} ){2}")
        result = frame.findall(text)
        return_val = []
        for gr in result:
            return_val.append(gr[2])
        return return_val
    
    def timeout(self):
        self.timeout_flag = False
        pass

    def load_init_cfg(self):
        try:
            with open("init_cfg.json") as complex_data:
                data = complex_data.read()
                json_cfg = json.loads(data)
                self.mim.port = json_cfg.get("port", "COM0")
                self.mim.serial_numbers = json_cfg.get("SN", ["A50285"])
        except FileNotFoundError:
            pass
        pass

    def save_init_cfg(self):
        cfg_dict = {"port": self.mim.port, "SN": self.mim.serial_numbers}
        with open("init_cfg.json", "w") as write_file:
            json.dump(cfg_dict, write_file, sort_keys=True, indent=4)
        pass

    def closeEvent(self, event):
        self.save_init_cfg()
        self.close()
        pass


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # os.environ["QT_SCALE_FACTOR"] = "1.0"
    #
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()  # и запускаем приложение
