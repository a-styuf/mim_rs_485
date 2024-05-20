import segmented_data
import cmd_gen as cg
import random


class MIM_RS485_MAP:
    def __init__(self, **kw):
        self.addr = kw.get('alias', 'NU')
        self.addr = kw.get('addr', 0x0C)
        self.id = kw.get('id', 0x00)
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
    MIM_RS485_MAP(alias="short_tmi",        addr=0x0C, id= 0, flag="data", data=None),
    MIM_RS485_MAP(alias="tmi",              addr=0x0C, id= 1, flag="data", data=None),
]

# id_list для тестирования сегментированных данных
full_data = [(i & 0xFF) for i in range(100)]
segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=0, data=full_data)
segmented_data_id_list = [  MIM_RS485_MAP(alias="segmented_data", addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list]

# id_list для тестирования отправки данных
tx_data_list = [cg.Tx_Data(module=i) for i in range(9, 10)]
for num, tx_d in enumerate(tx_data_list):
    tx_d.set_pay_load(bytes([tx_d.module] + [i for i in range(4)]))
tx_test_id_list = [ (MIM_RS485_MAP(alias="asp_tx_frame", addr=0x0C, id=20, flag="cmd", data=tx_d.form_packet())) 
                    for tx_d in tx_data_list]

# id_list для тестирования отправки данных
tx_data_list_raw = [cg.Tx_Data(module=i) for i in [9, 10]]
for num, tx_d in enumerate(tx_data_list_raw):
    tx_d.set_pay_load(bytes([tx_d.module] + [i for i in range(254)]))
segm_tx_test_id_list = []
for num, tx_d in enumerate(tx_data_list_raw):
    data_to_send = list(int.to_bytes(18, 1, byteorder="little") + tx_d.form_packet())
    segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=num, data=data_to_send)
    segm_tx_test_id_list.extend([  MIM_RS485_MAP(alias="segm_tx_frame", addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list])
    


# чтение настроек приемника и передатчика и применение настроек приемника
get_tx_cfg_id_list = [
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 16, flag="cmd", data=cg.Tx_Cfg(module=10).form_packet()),
    MIM_RS485_MAP(alias="get_cfg",           addr=0x0C, id= 17, flag="data", data=None),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 19, flag="cmd", data=cg.Rx_Cfg(module=10).form_packet()),
    MIM_RS485_MAP(alias="get_cfg",           addr=0x0C, id= 20, flag="data", data=None),
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[10, 0]).form_packet()),
]

# turn on receivers with default settings
rx_turn_on_id_list = [
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[1, 0]).form_packet()),
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[8, 0]).form_packet()),
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[9, 0]).form_packet()),
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[10, 0]).form_packet()),
]

turn_on_10th_moduleid_list = [
    MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[9, 0]).form_packet()),
]

cmd_test_id_list = [
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0x00, 0x00]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0x00, 0x00]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0xFF, 0xFF]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0xFF, 0xFF]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0xFF, 0xFF]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0xFF, 0xFF]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=1, param=[0xFF, 0xFF]).form_packet()),
    MIM_RS485_MAP(alias="resp_cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=3, param=[0x00, 0x00]).form_packet()),
    ]

rx_polling_id_list =    []
rx_polling_id_list += MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[1, 0]).form_packet()),
rx_polling_id_list += MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[8, 0]).form_packet()),
rx_polling_id_list += MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[9, 0]).form_packet()),
rx_polling_id_list += MIM_RS485_MAP(alias="apply cfg",          addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[10, 0]).form_packet()),
rx_polling_id_list += [ MIM_RS485_MAP(alias="rx_polling",        addr=0x0C, id= 22, flag="data", data=None),
                        MIM_RS485_MAP(alias="mfr_rx_polling",    addr=0x0C, id= 64, flag="data", data=None)]

time_stamp_test_id_list = [MIM_RS485_MAP(   alias="time_set",      
                                            addr=0x0C, 
                                            id= 2, 
                                            flag="cmd", 
                                            data=bytes.fromhex("B7 1D 77 65 9E 1C")
                                            )]

# ma like polling
ma_polling_id_list =    []
ma_polling_id_list += [ MIM_RS485_MAP(alias="rx_polling",        addr=0x0C, id= 22, flag="data", data=None)]

# mrf like polling
mrf_polling_id_list =    []
mrf_polling_id_list += [ MIM_RS485_MAP(alias="mfr_rx_polling",    addr=0x0C, id= 64, flag="data", data=None)]

# iss test 
full_data = [var & 0xFF for var in bytes.fromhex("15 13 00 46 01 09 00 01 00 00 00 00 B1 BC 33 01 00 00 00 80 E5 F9 FF 01 00 00 00 20 6C FB FF 01 00 00 00 C0 F2 FC FF 01 00 00 00 60 79 FE FF 01 00 00 00 00 00 00 00 01 00 00 00 A0 86 01 00 01 00 00 00 40 0D 03 00 01 00 00 00 E0 93 04 00 01 09 08 00 00 00 00 00 01 00 00 00 00 A1 BC 33 01 00 00 00 80 E5 F9 FF 01 00 00 00 20 6C FB FF 01 00 00 00 C0 F2 FC FF 01 00 00 00 60 79 FE FF 01 00 00 00 00 00 00 00 01 00 00 00 A0 86 01 00 01 00 00 00 40 0D 03 00 01 00 00 00 E0 93 04 00 01 09 08 00 00 00 00 00 01 00 00 00 C0 CA 89 36 01 00 00 00 80 E5 F9 FF 01 00 00 00 20 6C FB FF 01 00 00 00 C0 F2 FC FF 01 00 00 00 60 79 FE FF 01 00 00 00 00 00 00 00 01 00 00 00 A0 86 01 00 01 00 00 00 40 0D 03 00 01 00 00 00 E0 93 04 00 01 09 08 00 00 00 00 00 01 00 00 00 C0 CA 89 36 01 00 00 00 80 E5 F9 FF 01 00 00 00 20 6C FB FF 01 00 00 00 C0 F2 FC FF 01 00 00 00 60 79 FE FF 01 00 00 00 00 00 00 00 01 00 00 00 A0 86 01 00 01 00 00 00 40 0D 03 00 01 00 00 00 E0 93 04 00 01 09 08 00 00 00 00 00")]
segmented_data_list = segmented_data.segmented_data_data_list(id=65, seq_num=random.randint(0, 127), data=full_data)

iss_test_id_list = [
    MIM_RS485_MAP(alias="rx_req_cfg",       addr=0x0C, id=19, flag="cmd",  data=bytes.fromhex("11 00 06 00 09 00")),
    MIM_RS485_MAP(alias="rx_get_cfg",       addr=0x0C, id=20, flag="data",  data=None)
    ]
iss_test_id_list += [  
    MIM_RS485_MAP(alias="segmented_data",   addr=0x0C, id=65, flag="cmd", data=data) for data in segmented_data_list
    ]
iss_test_id_list += [
    # MIM_RS485_MAP(alias="apply cfg",        addr=0x0C, id= 3, flag="cmd", data=cg.Settings_Cmd(num=2, param=[9, 0]).form_packet()),
    MIM_RS485_MAP(alias="rx_req_cfg",       addr=0x0C, id=19, flag="cmd",  data=bytes.fromhex("11 00 06 00 09 00")),
    MIM_RS485_MAP(alias="rx_get_cfg",       addr=0x0C, id=20, flag="data",  data=None)
]