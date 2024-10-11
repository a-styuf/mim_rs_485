import mim
import time
from threading import Thread, Lock
from .transaction_list import *  # noqa: F403
from loguru import logger
from sx127x_gs.radio_controller import RadioController  # noqa: F401
import pandas as pd

pd.set_option('display.max_rows', None)

WORK_TIME       = 1800        # s
LIST_INTERVAL   = 1.0         # s
CMD_INTERVAL    = 1.0         # s


def interface_test(mim_dev, id_list, lock: Lock, work_time: float, list_interval: float, cmd_interval: float, parsing=False):
    #
    error_cnt = 0
    num = 0
    start_time = time.perf_counter()
    lock.acquire(), logger.info(f"\t{mim_dev.alias}: start"), lock.release() # type: ignore
    while (time.perf_counter() - start_time) < work_time:
        time.sleep(list_interval)    
        for id in id_list:
            transaction_start = time.perf_counter()
            tx_frame = mim_dev.request(addr=id.addr, id=id.id, mode=id.flag, data=id.data)
            lock.acquire(), logger.info(f"\t{mim_dev.alias}: tx_data {len(tx_frame)} (id={id.id}) {tx_frame.hex(' ').upper()}"), lock.release() # type: ignore
            #
            while mim_dev.ready_to_transaction is False:
                time.sleep(0.001)
            #
            rx_frame = mim_dev.get_last_data()
            if rx_frame:
                lock.acquire(), logger.info(f"\t{mim_dev.alias}: rx_data {len(rx_frame)} (id={id.id}) t={(time.perf_counter() - transaction_start):.3f}: {(rx_frame.hex(' ').upper())}; id <{mim_dev.check_frame(fr=rx_frame)}>"), lock.release() # type: ignore
                if (mim_dev.check_frame(fr=rx_frame) >= 0):
                    lock.acquire()
                    if(parsing):
                        logger.info(f"{(mim_dev.parc_data(rx_frame))}") 
                    lock.release()
                pass
            else:
                lock.acquire(), logger.info(f"\t{mim_dev.alias}: rx_error t={(time.perf_counter() - transaction_start):.3f}: rx_data (id={id.id})"), lock.release() # type: ignore
                error_cnt += 1
            time.sleep(cmd_interval)
        num += 1
        lock.acquire(), logger.info(f"\t{mim_dev.alias}:\t <{(time.perf_counter() - start_time):.3f}>s, num<{num:06d}>, rx_error_cnt {error_cnt}"), lock.release() # type: ignore
        # if error_cnt > 100:
        #     break
    lock.acquire(), logger.info(f"\t{mim_dev.alias}: finish <{(time.perf_counter() - start_time):.3f}>"), lock.release() # type: ignore
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
    mim_ma= mim.MimRS485Device(alias="MA", addr=0x01, serial_numbers=["A50285"], debug=False)
    mim_mfr = mim.MimRS485Device(alias="MFR", addr=0x02, port="COM40", debug=True)
    # mim_ma.open_id()
    # mim_ma.debug = False
    mim_ma.open_id()
    # mim_ma.open_port()
    # mim_mfr.debug = False
    #
    interface_list = [mim_ma, mim_mfr]
    # потоки тестирования
    logger.info(f"Инициализация")
    print_lock = Lock()
    #
    t_ma = Thread(target = interface_test, args = (interface_list[0], cmd_test_id_list, print_lock, 5.0, 0.0, 0.0), daemon=True)
    t_ma.start()
    t_ma.join()
    #
    logger.info(f"Тестирование окончено за {(time.perf_counter() - start_time):.3f}")