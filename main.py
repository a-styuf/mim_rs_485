import mim
import time
import crc
from threading import Thread, Lock
import segmented_data


class MIM_RS485_MAP:
    def __init__(self, **kw):
        self.addr = kw.get('alias', 'NU')
        self.addr = kw.get('addr', 0x0C)
        self.id =   kw.get('id', 0x00)
        self.flag = kw.get('flag', "data")
        self.data = kw.get('data', None)
    
id_list = [
    MIM_RS485_MAP(alias="short_tmi",        addr=0x0C, id= 0, flag="data", data=None),
    MIM_RS485_MAP(alias="tmi",              addr=0x0C, id= 1, flag="data", data=None),
    MIM_RS485_MAP(alias="set_time",         addr=0x0C, id= 2, flag="cmd", data=[0xFE for i in range(6)]),
    MIM_RS485_MAP(alias="write_settings",   addr=0x0C, id= 3, flag="cmd", data=[0xFE for i in range(128)]),
    MIM_RS485_MAP(alias="read_settings",    addr=0x0C, id= 4, flag="data", data=None),
    MIM_RS485_MAP(alias="sys_tmi",          addr=0x0C, id= 5, flag="data", data=None),
    MIM_RS485_MAP(alias="set_exp",          addr=0x0C, id= 6, flag="cmd", data=[0xFE for i in range(128)]),
    MIM_RS485_MAP(alias="read_exp",         addr=0x0C, id= 7, flag="data", data=None),
    MIM_RS485_MAP(alias="exp_tmi",          addr=0x0C, id= 8, flag="data", data=None),
    #
    MIM_RS485_MAP(alias="asp_status",       addr=0x0C, id=16, flag="data", data=None),
    MIM_RS485_MAP(alias="asp_data_rd",      addr=0x0C, id=17, flag="data", data=None),
    MIM_RS485_MAP(alias="asp_kwit_rd",      addr=0x0C, id=18, flag="data", data=None),
    MIM_RS485_MAP(alias="cfg_resp",         addr=0x0C, id=19, flag="cmd", data=[0xFE for i in range(4)]),
    MIM_RS485_MAP(alias="asp_data_wr",      addr=0x0C, id=20, flag="cmd", data=[0xFE for i in range(285)]),
    MIM_RS485_MAP(alias="pn_cfg_resp",      addr=0x0C, id=21, flag="data", data=None),
    MIM_RS485_MAP(alias="pn_cfg_wr",        addr=0x0C, id=22, flag="cmd", data=[0xFE for i in range(44)]),
    MIM_RS485_MAP(alias="gws_resp_p1",      addr=0x0C, id=23, flag="data", data=None),
    MIM_RS485_MAP(alias="gws_resp_p2",      addr=0x0C, id=24, flag="data", data=None),
    MIM_RS485_MAP(alias="gws_wr_p1",        addr=0x0C, id=25, flag="cmd", data=[0xFE for i in range(883)]),
    MIM_RS485_MAP(alias="gws_wr_p2",        addr=0x0C, id=26, flag="cmd", data=[0xFE for i in range(880)]),
    MIM_RS485_MAP(alias="gw_resp",          addr=0x0C, id=27, flag="data", data=None),
    MIM_RS485_MAP(alias="gw_wr",            addr=0x0C, id=28, flag="cmd", data=[0xFE for i in range(46)]),
    #
    MIM_RS485_MAP(alias="s_gw_resp",        addr=0x0C, id=32, flag="data", data=None),
    MIM_RS485_MAP(alias="s_gw_data_wr",     addr=0x0C, id=33, flag="cmd", data=[0xFE for i in range(304)]),
    #
    MIM_RS485_MAP(alias="exp_data_resp",    addr=0x0C, id=48, flag="cmd", data=[0xFE for i in range(16)]),
    MIM_RS485_MAP(alias="exp_data_rd",      addr=0x0C, id=49, flag="data", data=None),
    #
    MIM_RS485_MAP(alias="mfr_data_rd",      addr=0x0C, id=64, flag="data", data=[0x00 for i in range(15)]),
    MIM_RS485_MAP(alias="mfr_data_wr",      addr=0x0C, id=65, flag="cmd", data=[0xFE for i in range(64)])
]

mfr_id_list = [
    # MIM_RS485_MAP(alias="mfr_data_rd",      addr=0x0C, id=64, flag="data", data=None),
    MIM_RS485_MAP(alias="mfr_data_rd",      addr=0x0C, id=64, flag="data", data=[0x00 for i in range(15)]),
    MIM_RS485_MAP(alias="mfr_data_wr",      addr=0x0C, id=65, flag="cmd", data=[0xFE for i in range(64)])
]

ma_id_list = [
    # MIM_RS485_MAP(alias="short_tmi",        addr=0x0C, id= 0, flag="data", data=None),
    MIM_RS485_MAP(alias="tmi",              addr=0x0C, id= 1, flag="data", data=None),
]

full_data = [(i & 0xFF) for i in range(100)]
segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=0, data=full_data)
segmented_data_id_list = [  MIM_RS485_MAP(alias="segmented_data", addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list]


def interface_test(mim_dev, id_list, lock: Lock):
    work_time = 10  # s
    error_cnt = 0
    num = 0
    start_time = time.perf_counter()
    lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: start"), lock.release()
    while (time.perf_counter() - start_time) < work_time:
        time.sleep(1)    
        for id in id_list:
            transaction_start = time.perf_counter()
            tx_frame = mim_dev.request(addr=id.addr, id=id.id, mode=id.flag, data=id.data, )
            # lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: tx_data {len(tx_frame)} b (id={id.id}) {(tx_frame[:min(vis_limit, len(tx_frame))].hex(' ').upper())}", "..." if vis_limit < len(tx_frame) else ""), lock.release()
            #
            while mim_dev.ready_to_transaction is False:
                time.sleep(0.010)
            #
            rx_frame = mim_dev.get_last_data()
            if rx_frame:
                # lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: rx_data (id={id.id}) t={(time.perf_counter() - transaction_start):.3f} {(rx_frame[:min(vis_limit, len(rx_frame))].hex(' ').upper())}", "..." if vis_limit < len(rx_frame) else ""), lock.release()
                pass
            else:
                lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: rx_error t={(time.perf_counter() - transaction_start):.3f} rx_data (id={id.id})"), lock.release()
                error_cnt += 1
            time.sleep(0.050)
        num += 1
        lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}:\t <{(time.perf_counter() - start_time):.3f}>s, num<{num:06d}>, rx_error_cnt {error_cnt}"), lock.release()
        if error_cnt > 100:
            break
    lock.acquire(), print(mim.get_time(), f"\t{mim_dev.alias}: finish <{(time.perf_counter() - start_time):.3f}>"), lock.release()
    return

if __name__ == "__main__":

    error_cnt = 0
    vis_limit = 64
    #
    start_time = time.perf_counter()
    print(mim.get_time(), f"Начало тестирования интерфейсов")
    #
    mim_ma = mim.MimRS485Device(alias="MA", serial_numbers=["A50285"], debug=True)
    mim_mfr = mim.MimRS485Device(alias="MFR", addr=0x01, port="COM30", debug=True)
    mim_ma.open_id()
    mim_ma.debug = False
    mim_mfr.open_port()
    # mim_mfr.open_id()
    mim_mfr.debug = False
    interface_list = [mim_ma, mim_mfr]
    # потоки тестирования
    print_lock = Lock()
    t_ma = Thread(target = interface_test, args = (interface_list[0], id_list, print_lock), daemon=True)
    t_mrf = Thread(target = interface_test, args = (interface_list[1], id_list, print_lock), daemon=True)
    # Проверка команды зеркала
    t_ma.start()
    t_mrf.start()
    t_ma.join()
    t_mrf.join()
    #
    print(mim.get_time(), f"Тестирование окончено за {(time.perf_counter() - start_time):.3f}")    
