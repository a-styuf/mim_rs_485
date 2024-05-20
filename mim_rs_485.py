import mim
import time
import crc
from threading import Thread, Lock
import segmented_data
from transaction_list import *
from loguru import logger
from sx127x_gs.radio_controller import RadioController

WORK_TIME       = 1800        # s
LIST_INTERVAL   = 1.0         # s
CMD_INTERVAL    = 1.0         # s


def interface_test(mim_dev, id_list, lock: Lock, work_time: float, list_interval: float, cmd_interval: float):
    #
    error_cnt = 0
    num = 0
    start_time = time.perf_counter()
    lock.acquire(), logger.info(f"\t{mim_dev.alias}: start"), lock.release()
    while (time.perf_counter() - start_time) < work_time:
        time.sleep(list_interval)    
        for id in id_list:
            transaction_start = time.perf_counter()
            tx_frame = mim_dev.request(addr=id.addr, id=id.id, mode=id.flag, data=id.data)
            lock.acquire(), logger.info(f"\t{mim_dev.alias}: tx_data {len(tx_frame)} (id={id.id}) {tx_frame.hex(' ').upper()}"), lock.release()
            #
            while mim_dev.ready_to_transaction is False:
                time.sleep(0.010)
            #
            rx_frame = mim_dev.get_last_data()
            if rx_frame:
                lock.acquire(), logger.info(f"\t{mim_dev.alias}: rx_data {len(rx_frame)} (id={id.id}) t={(time.perf_counter() - transaction_start):.3f} {(rx_frame.hex(' ').upper())} crc {mim_dev.check_frame(fr=rx_frame)}"), lock.release()
                pass
            else:
                lock.acquire(), logger.info(f"\t{mim_dev.alias}: rx_error t={(time.perf_counter() - transaction_start):.3f} rx_data (id={id.id})"), lock.release()
                error_cnt += 1
            time.sleep(cmd_interval)
        num += 1
        lock.acquire(), logger.info(f"\t{mim_dev.alias}:\t <{(time.perf_counter() - start_time):.3f}>s, num<{num:06d}>, rx_error_cnt {error_cnt}"), lock.release()
        # if error_cnt > 100:
        #     break
    lock.acquire(), logger.info(f"\t{mim_dev.alias}: finish <{(time.perf_counter() - start_time):.3f}>"), lock.release()
    return


if __name__ == "__main__":
    logger.add("loguru.log")
    #
    error_cnt = 0
    vis_limit = 64
    #
    start_time = time.perf_counter()
    logger.info(f"Начало тестирования интерфейсов")
    #
    # radio = RadioController(interface="Serial")
    # radio.connect('COM41')
    # radio.send_single([0, 0])
    # time.sleep(2.0)
    #
    mim_ma = mim.MimRS485Device(alias="MA", addr=0x03, serial_numbers=["A50285"], debug=True)
    mim_mfr = mim.MimRS485Device(alias="MFR", addr=0x01, port="COM47", debug=True)
    # mim_ma.open_id()
    # mim_ma.debug = False
    # mim_mfr.open_id()
    mim_mfr.open_port()
    mim_mfr.debug = False
    #
    interface_list = [mim_ma, mim_mfr]
    # потоки тестирования
    print_lock = Lock()
    t_ma = Thread(target = interface_test, args = (interface_list[0], ma_id_list, print_lock, 1.0, 1.0, 1.0), daemon=True)
    # t_ma.start()
    logger.info(f"Инициализация")
    t_mrf = Thread(target = interface_test, args = (interface_list[1], turn_on_10th_moduleid_list, print_lock, 1.0, 1.0, 1.0), daemon=True)
    t_mrf.start()
    t_mrf.join()
    #
    # time.sleep(5.0)
    # radio.send_single([0, 1, 2, 3])
    # time.sleep(5.0)
    #
    logger.info(f"Запуск опроса")
    t_mrf = Thread(target = interface_test, args = (interface_list[1], ma_polling_id_list, print_lock, 1.0, 0.2, 0.2), daemon=True)
    t_mrf.start()
    t_mrf.join()
    #
    logger.info(f"Ожидание 8-ми минут")
    time.sleep(8*60)
    #
    # radio.send_single([5, 6, 7, 8])
    # time.sleep(5.0)
    #
    logger.info(f"Запуск опроса")
    t_mrf = Thread(target = interface_test, args = (interface_list[1], ma_polling_id_list, print_lock, 1.0, 0.2, 0.2), daemon=True)
    t_mrf.start()
    t_mrf.join()
    #
    logger.info(f"Тестирование окончено за {(time.perf_counter() - start_time):.3f}")