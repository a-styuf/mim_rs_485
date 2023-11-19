import segmented_data
import tx_data as tx

class MIM_RS485_MAP:
    def __init__(self, **kw):
        self.addr = kw.get('alias', 'NU')
        self.addr = kw.get('addr', 0x0C)
        self.id =   kw.get('id', 0x00)
        self.flag = kw.get('flag', "data")
        self.data = kw.get('data', [])
    
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

# id_list для тестирования сегментированных данных
full_data = [(i & 0xFF) for i in range(100)]
segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=0, data=full_data)
segmented_data_id_list = [  MIM_RS485_MAP(alias="segmented_data", addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list]

# id_list для тестирования отправки данных
tx_data_list = [tx.Tx_Data(module=i) for i in range(9, 10)]
for num, tx_d in enumerate(tx_data_list):
    tx_d.set_pay_load(bytes([tx_d.module] + [i for i in range(254)]))
tx_test_id_list = [ (MIM_RS485_MAP(alias="asp_tx_frame", addr=0x0C, id=20, flag="cmd", data=tx_d.form_packet())) 
                    for tx_d in tx_data_list]

# id_list для тестирования отправки данных
tx_data_list = [tx.Tx_Data(module=i) for i in [9, 9]]
for num, tx_d in enumerate(tx_data_list):
    tx_d.set_pay_load(bytes([tx_d.module] + [i for i in range(254)]))
segm_tx_test_id_list = []
for num, tx_d in enumerate(tx_data_list):
    data_to_send = list(int.to_bytes(20, 1) + tx_d.form_packet())
    segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=num, data=data_to_send)
    segm_tx_test_id_list.extend([  MIM_RS485_MAP(alias="segm_tx_frame", addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list])

