import serial
import serial.serialutil
import serial.tools.list_ports
import threading
import time
import copy

from serial.tools.list_ports_common import ListPortInfo
import mim_parser
from loguru import logger
import crc16_ccitt_table


class MimRS485Device(serial.Serial):
    def __init__(self, **kw) -> None:
        serial.Serial.__init__(self, parity = serial.PARITY_EVEN)
        #
        self.serial_numbers = kw.get("serial_numbers", [])  # это лист возможных серийников!!! (не строка)
        self.baudrate = kw.get("baudrate", 921600)
        self.timeout = kw.get("timeout", 0.002)
        self.port = kw.get('port', "COM0")
        self.debug = kw.get('debug', True)
        self.addr = kw.get("addr", 0x00)
        self.alias = kw.get("alias", "NU")
        #
        # self.crc_calculator = Calculator(Crc8.CCITT)
        self.row_data:bytearray 
        self.read_timeout = 0.3
        self.request_num = 0
        self.crc_check = True

        # общие переменные
        self.com_queue: list = []  # очередь отправки
        self.request_num = 0
        self.nansw = 0  # неответы
        self.answer_data: list = []
        self.req_number = 0
        self.last_answer_data: bytearray = bytearray()
        self.answer_data_buffer: list = []
        self.read_data : bytearray = bytearray()
        self.read_flag = 0
        self.state_string: dict[int, str] = {
            -3: "Связь потеряна",
            -2: "Устройство не отвечает",
            -1: "Не удалось установить связь",
            +0: "Подключите устройство",
            +1: "Связь в норме",
        }
        self.state = 0
        self.ready_to_transaction = True
        self.serial_log_buffer: list = []
        self.mim_log_buffer: list = []
        # для работы с потоками
        self._close_event = threading.Event()
        self.read_write_thread = threading.Thread(target=self.thread_function, args=(), daemon=True)

        self.log_lock = threading.Lock()
        self.com_send_lock = threading.Lock()
        self.ans_data_lock = threading.Lock()

    def open_id(self) -> bool:  # функция для установки связи
        com_list: list[ListPortInfo] = serial.tools.list_ports.comports()
        for com in com_list:
            self._print("Find:", str(com), com.serial_number)
            for serial_number in self.serial_numbers:
                self._print("ID comparison:", com.serial_number, serial_number)
                if com.serial_number and len(serial_number) >= 4:
                    find_len: int = min(len(com.serial_number), len(serial_number))
                    if com.serial_number[:find_len] == serial_number[:find_len]:
                        self._print("Connection to:", com.device)
                        self.port = com.device
                        try:
                            self.open()
                            self._print("Success connection!")
                            try:
                                self._close_event.clear()
                                self.read_write_thread.start()
                            except Exception:
                                pass
                            self.state = 1
                            self.nansw = 0
                            return True
                        except serial.serialutil.SerialException as error:
                            self._print("Fail connection")
                            self._print(error)
        self.state = -1
        return False
    
    def open_port(self) -> bool:  # функция для установки связи
        self._print("Connection to ", self.port)
        try:
            self.open()
            self._print("Success connection!")
            try:
                self._close_event.clear()
                self.read_write_thread.start()
            except Exception:
                pass
            self.state = 1
            self.nansw = 0
            return True
        except serial.serialutil.SerialException as error:
            self._print("Fail connection")
            self._print(error)
            self.state = -1
        return False

    def _print(self, *args) -> None:
        print_str: str = ""
        if self.debug:
            for arg in args:
                print_str += " " + str(arg)
            logger.info(print_str)

    def close_id(self) -> None:
        self._print("Try to close COM-port <0x%s>:" % self.port)
        self._close_event.set()
        self.close()
        self.state = 0
        pass

    def reconnect(self) -> None:
        self.close_id()
        self._print(f"Try to close: is_open is <{self.is_open}>")
        time.sleep(0.1)
        self.open_id()
        self._print(f"Try to open: is_open is <{self.is_open}>")
        self._print(self)
        
    def form_frame(self, addr=0x0C, id=0, mode="cmd", fr_data = None) -> bytes: # type: ignore
        if fr_data is None:
            fr_data: list = []
        frame: list = []
        #
        if mode == "cmd":
            flag = 0x12
        if mode == "data":
            flag = 0x04
        data_len = 1 + len(fr_data)
        #
        frame.append(0xF0)
        frame.append(addr)
        frame.append(self.addr)
        frame.append(flag)
        frame.append((data_len >> 8) & 0xFF)
        frame.append((data_len >> 0) & 0xFF)
        frame.append(id)
        frame.extend(fr_data)
        frame.append(crc16_ccitt_table.crc8ccitt(bytes(frame[1:]), 0x00))
        frame.append(0x0F)
        #
        return bytes(frame)
    
    def check_frame(self, fr : list|bytes|None=b"") -> int:
        """_summary_

        Args:
            fr (list, optional): _description_. Defaults to [].

        Returns:
            int: <0 - Error, >=0 - ID
        """
        if fr is None:
            return 0
        if fr[0] == 0xF0 and fr[-1] == 0x0F:
            frame_len: int = len(fr)
            if frame_len >= 9:
                crc: int = crc16_ccitt_table.crc8ccitt(bytes(fr[1:-2]), 0x00)
                if crc == fr[-2]:
                    return int(fr[6])
                else:
                    return -3
            else:
                return -2
        else:
            return -1
        
    def request(self, addr=0x0C, id=0, mode="cmd", data=None) -> bytes:
        tx_frame = bytes(self.form_frame(addr=addr, id=id, mode=mode, fr_data=data))
        #
        with self.com_send_lock:
            self.com_queue.append(tx_frame)
            self.ready_to_transaction = False
        with self.log_lock:
            self.mim_log_buffer.append(tx_frame)
        self._print(f"Try to send command ({(tx_frame.hex(' ').upper())}):")
        return tx_frame

    def thread_function(self) -> None:
        #try:
        while True:
            nansw = 0
            if self.is_open is True:
                time.sleep(0.001)
                # отправка команд
                if self.com_queue:
                    self.ready_to_transaction = False
                    with self.com_send_lock:
                        packet_to_send = self.com_queue.pop(0)
                        data_to_send = packet_to_send
                    if self.in_waiting:
                        read_data = self.read(self.in_waiting)
                        #self._print("In input buffer %d bytes" % len(read_data))
                        print(f"{self.alias} In input buffer {len(read_data)} bytes", read_data.hex(" ").upper())
                    try:
                        #self.read(self.in_waiting)
                        self.write(data_to_send)
                        self._print("Send packet: ", data_to_send.hex(" ").upper())
                        step_num = 0
                        nansw = 1
                    except serial.serialutil.SerialException as error:
                        self.state = -3
                        self._print("Send error: ", error)
                        pass
                    with self.log_lock:
                        self.serial_log_buffer.append(get_time() + bytes_array_to_str(bytes(data_to_send)))
                    # прием ответа: ждем ответа timeout ms только в случае rtr=1
                    buf = bytearray(b"")
                    read_data = bytearray(b"")
                    time_start: float = time.perf_counter()
                    while 1:
                        time.sleep(0.001)
                        step_num += 1
                        timeout: float = time.perf_counter() - time_start
                        if timeout >= self.read_timeout:
                            break
                        try:
                            read_data: bytes | None = self.read_all()
                            #self._print("Receive data: ", read_data)
                        except (TypeError, serial.serialutil.SerialException, AttributeError) as error:
                            self.state = -3
                            #self._print("Receive error: ", error)
                            pass
                        if read_data:
                            self._print("Receive data (%d) with timeout <%.3f>: " % (len(read_data), self.timeout), read_data.hex(" ").upper())
                            with self.log_lock:
                                self.serial_log_buffer.append(get_time() + read_data.hex(" ").upper())
                            read_data = buf + bytes(read_data)  # прибавляем к новому куску старый кусок
                            #self._print("Data to process: ", read_data.hex(" ").upper())
                            if len(read_data) >= 6:
                                if read_data[0] == 0xF0:
                                    data_len: int = int.from_bytes(read_data[4:6], "big")
                                    # print(f"{self.alias} N={step_num}: expected = {data_len + 6 + 2} ({int.from_bytes(read_data[4:6], 'big')} 0x{read_data[4:6].hex(' ').upper()}), real_len = {len(read_data)}")
                                    if len(read_data) == data_len + 6 + 2:  # проверка на достаточную длину приходящего пакета
                                        nansw -= 1
                                        self.state = 1
                                        self.answer_data.append(read_data)
                                        self.last_answer_data: bytearray = read_data
                                        read_data = b""
                                        break
                                    elif len(read_data) > (data_len + 6 + 2):
                                        buf: bytearray= read_data
                                        # print(f"{self.alias}: {buf.hex(' ').upper()}")
                                        read_data = bytearray(b"")
                                    else:
                                        buf = read_data
                                        # print(f"{self.alias}: {buf.hex(' ').upper()}")
                                        read_data = bytearray(b"")
                                else:
                                    buf = read_data[1:]
                                    read_data = bytearray(b"")
                            else:
                                buf = read_data
                                read_data = bytearray(b"")
                            pass
                        else:
                            pass
                else:
                    self.ready_to_transaction = True
            else:
                pass
            if nansw == 1:
                self.state = -3
                self.nansw += 1
                self._print("Timeout error")
                self.ready_to_transaction = True
            if self._close_event.is_set() is True:
                self._close_event.clear()
                self._print("Close usb_can read thread")
                return
        # except Exception as error:
        #     self._print("Tx thread ERROR: " + str(error))
        # pass

    def get_mim_log(self) -> list:
        log = None
        with self.log_lock:
            log = copy.deepcopy(self.mim_log_buffer)
            self.can_mim_buffer = []
        return log

    def get_serial_log(self):
        log = None
        with self.log_lock:
            log = copy.deepcopy(self.serial_log_buffer)
            self.serial_log_buffer = []
        return log

    def get_data(self) -> list:
        data:list = []
        with self.ans_data_lock:
            if self.answer_data:
                for i in range(len(self.answer_data)):
                    try:
                        data.append(self.answer_data.pop(-1))
                    except IndexError:
                        pass
        return data

    def get_last_data(self) -> bytes:
        with self.ans_data_lock:
            if self.last_answer_data:
                data: bytearray = self.last_answer_data
                self.last_answer_data = bytearray()
            else:
                data = bytearray()
        return data

    def state_check(self) -> tuple:
        state_str: str = self.state_string[self.state]
        if self.state > 0:
            state_color = "seagreen"
        elif self.state < 0:
            state_color = "orangered"
        else:
            state_color = "gray"
        return state_str, state_color

    def parc_data(self, data: bytes) -> str:
        parc_str: str = ""
        id: int = self.check_frame(list(data))
        if id == 0:
            frame: mim_parser.Frame = mim_parser.ID0
        elif id == 1:
            frame = mim_parser.ID1
        elif id == 4:
            frame = mim_parser.ID4
        else:
            frame = bytearray()
            parc_str += "undefine frame"
            pass
        if frame:
            parc_str += str(frame.parse(data[7:-2]))
        else:
            parc_str += f"It isn't a frame. Error <{id:d}>"
        return parc_str

def get_time() -> str:
    return time.strftime("%H-%M-%S", time.localtime()) + "." + ("%.3f:" % time.perf_counter()).split(".")[1]


def str_to_list(send_str : str) -> list:  # функция, которая из последовательности шестнадцатеричных слов в строке без
    send_list: list = []  # идентификатора 0x делает лист шестнадцатеричных чисел
    send_split_result: list = send_str.split(' ')
    for i, ch in enumerate(send_split_result):
        send_split_result[i] = ch
        send_list.append(int(send_str[i], 16))
    return send_list


def bytes_array_to_str(bytes_array) -> str:
    bytes_string: str = ""
    for num, ch in enumerate(bytes_array):
        byte_str: str = "" if num % 2 else " "
        byte_str += ("%02X" % bytes_array[num])
        bytes_string += byte_str
    return bytes_string


if __name__ == "__main__":
    mim_ma = MimRS485Device(alias="MA", serial_numbers=["A50285"], debug=False)
    # mim_mfr = MimRS485Device(alias="MFR", port="COM30", debug=True)
    mim_ma.open_id()
    mim_ma.debug = False
    # mim_mfr.open_port()
    # mim_mfr.debug = False
    interface_list = [mim_ma]
    debug=True
    # Проверка команды зеркала
    for interface in interface_list:
        for k in range(1):
            print(get_time(), f"{interface.alias}: tx_data {(interface.request(addr=0x0C, id=0, mode='data').hex(' ').upper())}")
            while interface.ready_to_transaction is False:
                pass
            print(get_time(), f"{interface.alias}: rx_data {(interface.get_last_data().hex(' ').upper())}")
        pass
