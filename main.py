import mim
import time
import crc
from threading import Thread, Lock
import segmented_data
from transaction_list import *

WORK_TIME   = 1000  # s
INTERVAL    = 2    # s

def interface_test(mim_dev, id_list, lock: Lock):
    work_time = WORK_TIME  # s
    error_cnt = 0
    num = 0
    start_time = time.perf_counter()
    lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: start"), lock.release()
    while (time.perf_counter() - start_time) < work_time:
        time.sleep(INTERVAL)    
        for id in id_list:
            transaction_start = time.perf_counter()
            tx_frame = mim_dev.request(addr=id.addr, id=id.id, mode=id.flag, data=id.data)
            lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: tx_data {len(tx_frame)} (id={id.id}) {(tx_frame[:min(vis_limit, len(tx_frame))].hex(' ').upper())}",
                                "..." if vis_limit < len(tx_frame) else "", 
                                (f"{tx_frame[(len(tx_frame) - 10) : len(tx_frame)].hex(' ').upper()}") if vis_limit < len(tx_frame) else ""), lock.release()
            #
            while mim_dev.ready_to_transaction is False:
                time.sleep(0.010)
            #
            rx_frame = mim_dev.get_last_data()
            if rx_frame:
                lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: rx_data {len(rx_frame)} (id={id.id}) t={(time.perf_counter() - transaction_start):.3f} {(rx_frame[:min(vis_limit, len(rx_frame))].hex(' ').upper())}", 
                                    "..." if vis_limit < len(rx_frame) else "", 
                                    (f"{rx_frame[(len(rx_frame) - 10) : len(rx_frame)].hex(' ').upper()}") if vis_limit < len(rx_frame) else "",
                                    f"crc {mim_dev.check_frame(fr=rx_frame)}"), lock.release()
                # print(rx_frame.hex(' ').upper())
                pass
            else:
                lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: rx_error t={(time.perf_counter() - transaction_start):.3f} rx_data (id={id.id})"), lock.release()
                error_cnt += 1
            time.sleep(0.050)
        num += 1
        lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}:\t <{(time.perf_counter() - start_time):.3f}>s, num<{num:06d}>, rx_error_cnt {error_cnt}"), lock.release()
        # if error_cnt > 100:
        #     break
    lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: finish <{(time.perf_counter() - start_time):.3f}>"), lock.release()
    return

if __name__ == "__main__":

    error_cnt = 0
    vis_limit = 64
    #
    start_time = time.perf_counter()
    print(mim.get_time(), f"Начало тестирования интерфейсов")
    #
    mim_ma = mim.MimRS485Device(alias="MA", addr=0x03, serial_numbers=["A50285"], debug=True)
    mim_mfr = mim.MimRS485Device(alias="MFR", addr=0x01, port="COM33", debug=False)
    mim_ma.open_id()
    mim_ma.debug = False
    mim_mfr.open_port()
    # mim_mfr.open_id()
    mim_mfr.debug = False
    interface_list = [mim_ma, mim_mfr]
    # потоки тестирования
    print_lock = Lock()
    # t_ma = Thread(target = interface_test, args = (interface_list[0], segmented_data_id_list, print_lock), daemon=True)
    # t_mrf = Thread(target = interface_test, args = (interface_list[1], tx_test_id_list, print_lock), daemon=True)
    t_mrf = Thread(target = interface_test, args = (interface_list[1], segm_tx_test_id_list, print_lock), daemon=True)
    # Проверка команды зеркала
    # t_ma.start()
    t_mrf.start()
    # t_ma.join()
    t_mrf.join()
    #
    print(mim.get_time(), f"Тестирование окончено за {(time.perf_counter() - start_time):.3f}")    
