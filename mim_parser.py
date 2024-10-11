
from datetime import datetime, timedelta
from math import nan
import struct
from typing import Literal
from bytes_parser.frame_struct import Frame, SubFrame, Row, Bit


def devider(field: Row) -> float:
    result: float = int.from_bytes(field.raw_val, "little") / 256
    return result


def version_parser(field: Row) -> str:
    value: bytes = field.raw_val
    return f'{value[0]}.{value[1]}.{value[2]}'


def time_format(field: Row) -> str:
    timestamp: int = struct.unpack('<I', field.raw_val)[0]
    dt = datetime(2000, 1, 1, 0, 0, 0, 0) + timedelta(seconds=timestamp)
    return dt.isoformat(' ', 'seconds')


def float_unpack(field: Row) -> float:
    if field.raw_val == 0xFEFEFEFE.to_bytes(4):
        return nan
    elif len(field.raw_val):
        return struct.unpack("<f", field.raw_val)[0]
    else:
        return 0

def id_loc(field: Row):
    return field.raw_val[0]


header: list[Row] = [
    Row('LABEL', 2, 'X'),
    Row('ID_DEV', 2),
    Row('ID_LOC', 2, 'X', parser=id_loc),
    Row('FRAME_NUM', 2),
    Row('FR_TIME', 4, 's', parser=time_format)
]

ID0: Frame = Frame('ID0', [
    Row('LABEL', 1, 'X'),
    Row('MIM_STATUS', 2, 'X', min_value=1, max_value=1),
    Row('ERR_STATUS', 2, 'X'),
    Row('RX_FIFO_CNT', 2),
    Row('RX_TOTAL_CNT', 4),
    Row('TX_TOTAL_CNT', 4),
    Row('CRC8', 1, 'X'),
], 'little')

segment_cmd_status = [
    Row('SEGM_ERR_CNTER', 1),
    Row('SEGM_STATUS', 1, 'X'),
    Row('SEGM_DATA_CNTER', 2),
    Row('SEGM_TRANS_CNTER', 2),
    Row('SEGM_DATA_LEN', 2),
]

mim_err = [
    Row('MIM_STATUS', 2, 'X',
        bit_fields={0: Bit('WORKING', True),
                    1: Bit('S_TX', False),
                    2: Bit('EXP_MODE', False),
                    8: Bit('RX_BUF_NOT_EMPTY', False),
                    9: Bit('TX_BUF_NOT_EMPTY', False)},
        min_value=1, max_value=1),
    Row('ERR_STATUS', 2, 'X',
        bit_fields={0: Bit('PWR_ERR', False),
                    1: Bit('INTERFACE_1_ERR', False),
                    2: Bit('INTERFACE_2_ERR', False),
                    3: Bit('INTERNAL_BUS_ERR', False),
                    4: Bit('RX_OVERFLOW_ERR', False),
                    5: Bit('TX_OVERFLOW_ERR', False),
                    6: Bit('SINGLE_CMD_ERR', False),
                    7: Bit('EXP_PARAM_ERR', False)}),
]

ID1: Frame = Frame('ID1', [
    *SubFrame(header),
    *SubFrame(mim_err),
    Row('ERR_CNT', 2, max_value=0),
    Row('RX_FIFO_CNT', 2),
    Row('RX_TOTAL_CNT', 4),
    Row('TX_TOTAL_CNT', 4),
    Row('RX_LOST_CNT', 4),
    Row('TX_LOST_CNT', 4),
    Row('PWR_STATUS', 2, 'X', max_value=0,
        bit_fields={0: Bit('INTERFACE', False),
                    **{i: Bit(f'RADIO_{i}', False) for i in range(1, 14)}}),
    Row('PWR_STATE', 2, 'X', min_value=0x3FFF, max_value=0x3FFF,
        bit_fields={0: Bit('INTERFACE', True),
                    **{i: Bit(f'RADIO_{i}', True) for i in range(1, 14)}}),
    Row('PWR_CH_PRES', 2, 'X', min_value=0x3FFF, max_value=0x3FFF,
        bit_fields={0: Bit('INTERFACE', True),
                    **{i: Bit(f'RADIO_{i}', True) for i in range(1, 14)}}),
    Row('Voltage0', 2, '.2f', parser=devider),
    *[Row(f'Voltage{i}', 2, '.2f', parser=devider, max_value=5.2, min_value=4.5)
      for i in range(1, 14)],
    Row('Current0', 2, '.2f', parser=devider),
    *[Row(f'Current{i}', 2, '.2f', parser=devider,
          max_value=4 if i in [1, 3, 5, 7, 9, 10, 11, 12, 13] else 2,
          min_value=0.1)
      for i in range(1, 14)],
    *SubFrame(segment_cmd_status, prefix='1_'),
    *SubFrame(segment_cmd_status, prefix='2_'),
    Row('NAND_ID', 6, 'X', byte_order='big'),
    Row('RESERVE', 6, 'X'),
    Row('CRC16', 2, 'X'),
], 'little')


system_data_1: list[Row] = [x for i in range(6) for x in [
    Row(f'SELF_ID_{i + 1}', 1, 'X'),
    Row(f'RESERVE_{i + 1}', 1, 'X'),
    Row(f'STATUS_{i + 1}', 2, 'X',
        bit_fields={0:  Bit('WORKING', True),
                    1:  Bit('INTERNAL_BUS_ERR', False),
                    2:  Bit('RX_BUF_NOT_EMPTY', False),
                    3:  Bit('TX_BUF_NOT_EMPTY', False),
                    4:  Bit('VOLTAGE_ERR', False),
                    5:  Bit('PWR_ERR', False),
                    6:  Bit('MOSFET_ERR', False),
                    7:  Bit('UNKNOW_PWR_ERR', False),
                    8:  Bit('TX_1_ERR', False),
                    9:  Bit('TX_2_ERR', False),
                    10: Bit('TX_3_ERR', False),
                    11: Bit('TX_4_ERR', False),
                    12: Bit('RX_BUF_OVERFLOW', False),
                    13: Bit('TX_BUF_OVERFLOW', False),
                    15: Bit('UNKNOWN_ERR', False)}),
    Row(f'ERR_CNT_{i + 1}', 2, 'X', max_value=0),
    Row(f'U5V0_{i + 1}', 2, '.2f', parser=devider, max_value=5.2, min_value=4.5),
    Row(f'U3V3_{i + 1}', 2, '.2f', parser=devider, max_value=3.6, min_value=3),
    Row(f'CURRENT_{i + 1}', 2, '.2f', parser=devider,
        max_value=4 if i in [1, 3, 5] else 2,
        min_value=0.1),
    Row(f'RX_CNT_{i + 1}', 2, 'X'),
    Row(f'TX_CNT_{i + 1}', 2, 'X'),
]]

system_data_2: list[Row] = [x for i in range(7) for x in [
    Row(f'SELF_ID_{i + 7}', 1, 'X'),
    Row(f'RESERVE_{i + 7}', 1, 'X'),
    Row(f'STATUS_{i + 7}', 2, 'X',
        bit_fields={0:  Bit('WORKING', True),
                    1:  Bit('INTERNAL_BUS_ERR', False),
                    2:  Bit('RX_BUF_NOT_EMPTY', False),
                    3:  Bit('TX_BUF_NOT_EMPTY', False),
                    4:  Bit('VOLTAGE_ERR', False),
                    5:  Bit('PWR_ERR', False),
                    6:  Bit('MOSFET_ERR', False),
                    7:  Bit('UNKNOW_PWR_ERR', False),
                    8:  Bit('TX_1_ERR', False),
                    9:  Bit('TX_2_ERR', False),
                    10: Bit('TX_3_ERR', False),
                    11: Bit('TX_4_ERR', False),
                    12: Bit('RX_BUF_OVERFLOW', False),
                    13: Bit('TX_BUF_OVERFLOW', False),
                    15: Bit('UNKNOWN_ERR', False)}),
    Row(f'ERR_CNT_{i + 7}', 2, 'X', max_value=0),
    Row(f'U5V0_{i + 7}', 2, '.2f', parser=devider, max_value=5.2, min_value=4.5),
    Row(f'U3V3_{i + 7}', 2, '.2f', parser=devider, max_value=3.6, min_value=3),
    Row(f'CURRENT_{i + 7}', 2, '.2f', parser=devider,
        max_value=4 if i in [7, 9, 10, 11, 12, 13] else 2,
        min_value=0.1),
    Row(f'RX_CNT_{i + 7}', 2, 'X'),
    Row(f'TX_CNT_{i + 7}', 2, 'X'),
]]

ID4: Frame = Frame('ID4', [
    *SubFrame(header),
    Row('SELF_ID', 1, 'X'),
    Row('RESERVE', 1, 'X'),
    *SubFrame(mim_err),
    Row('ERR_CNT', 2, max_value=0),
    Row('RESERVE', 4, 'X'),
    Row('VER', 3, 'S', representer=version_parser),
    Row('RESERVE', 1, 'X'),
    *SubFrame(system_data_1),
    Row('RESERVE', 2, 'X'),
    Row('CRC16', 2, 'X'),
    *SubFrame(header),
    *SubFrame(system_data_2),
    Row('RESERVE2', 2, 'X'),
    Row('CRC16_2', 2, 'X'),
], 'little')

ID6: Frame = Frame('ID7', [
    Row('HEADER', 2, 'X'),
    Row('CMD_NUM', 2),
    Row('STEP_NUM', 2),
    Row('PERIOD_S', 2),
    Row('START_BLOCK', 4),
    Row('RESERVE', 1),
    Row('FRAME_TO_SAVE', 1),
    Row('RESERVE', 18),
], 'little')

exp_report_body: list = [
    Row('STATE', 1),
    Row('STATUS', 1, 'X',
        bit_fields={0: Bit('WORKING', True),
                    1: Bit('ERROR', False),
                    2: Bit('EMPTY_TX_BUF', False),
                    3: Bit('RX_ERR', False),
                    4: Bit('RUN_ERR', False),
                    5: Bit('RX_BUF_OVERFLOW', False),
                    6: Bit('SAVE_BUF_OVERFLOW', False)}),
    Row('ERROR_CNT', 2),
    Row('STEP_NUM', 2),
    Row('STEP_NUM_MAX', 2),
    Row('PERIOD_S', 2),
    Row('DATA_LEN', 1),
    Row('FRAME_TO_SAVE', 1),
    Row('START_BLOCK', 4),
    Row('RX_FRAME_NUM', 4),
    Row('LINE_READ_ERROR', 4),
    Row('LINE_WRITE_ERROR', 4),
    Row('UNIQ_TX_ID', 4, 'X'),
    Row('TX_FRAME_CNTER', 4),
    Row('RX_FRAME_CNTER', 4),
    Row('RX_SAVED_FRAME_CNTER', 4),
    Row('RESERVE', 70, 'X'),
]

ID7: Frame = Frame('ID7', [
    *SubFrame(header),
    *SubFrame(exp_report_body),
    Row('CRC16', 2, 'X'),
], 'little')

tx_params = [
    Row('BW', 1),
    Row('SF', 1),
    Row('CR', 1),
    Row('CRC_EN', 1),
    Row('LDRO', 1),
    Row('SYNC', 1),
    Row('IQ_INVERT', 1, 'X'),
    Row('RESERVE', 1, 'X'),
    Row('FREQUENCY', 4),
    Row('TX_POWER', 1),
    Row('DISABLE_AMPL', 1),
    Row('RESERVE_2', 2, 'X'),
]

ID17: Frame = Frame('ID17', [
    Row('PACKET_TYPE', 2, 'X'),
    Row('PACKET_SIZE', 2),
    Row('MODULE', 1),
    Row('RESERVE_1', 9, 'X'),
    *SubFrame(tx_params)
], 'little')

standart_channel: list[Row] = [
    Row('ENABLE', 1),
    Row('RESERVE', 3),
    Row('IF_FREQ', 4, signed=True),
]

service_channel: list[Row] = [
    Row('ENABLE', 1),
    Row('SF', 1),
    Row('BW', 1),
    Row('RESERVE', 1),
    Row('IF_FREQ', 4),
    # size = 8
]

module_settings: list[Row] = [
    Row('ENABLE', 1),
    Row('LDRO', 1),
    Row('SYNC', 1),
    Row('RESERVE_1', 1, 'X'),
    Row('FREQUENCY', 4),
    *SubFrame(standart_channel, postfix='_1'),
    *SubFrame(standart_channel, postfix='_2'),
    *SubFrame(standart_channel, postfix='_3'),
    *SubFrame(standart_channel, postfix='_4'),
    *SubFrame(standart_channel, postfix='_5'),
    *SubFrame(standart_channel, postfix='_6'),
    *SubFrame(standart_channel, postfix='_7'),
    *SubFrame(standart_channel, postfix='_8'),
    *SubFrame(service_channel, postfix='_SER')
    # size = 80
]


ID20: Frame = Frame('ID20', [
    Row('PACKET_TYPE', 2, 'X'),
    Row('PACKET_SIZE', 2),
    Row('MODULE', 1),
    Row('RESERVE_1', 1, 'X'),
    *(module_settings * 4),
    # size = 326
], 'little')


ID22: Frame = Frame('ID22', [
    Row('PACKET_TYPE', 2, 'X'),
    Row('PACKET_SIZE', 2),
    Row('TOT_SIZE', 2),
    Row('FREQ_HZ', 4),
    Row('FREQ_OFFSET', 4, signed=True),
    Row('IF_CHAN', 1),
    Row('STATUS', 1),
    Row('COUNT_US', 4),
    Row('DEV_ID', 1),
    Row('MODEM_ID', 1),
    Row('MODULATION', 1),
    Row('BW', 1),
    Row('SF', 1),
    Row('CR', 1),
    Row('RSSI_C', 4, '.2f', parser=float_unpack),
    Row('RSSI_S', 4, '.2f', parser=float_unpack),
    Row('SNR', 4, '.2f', parser=float_unpack),
    Row('SNR_MIN', 4, '.2f', parser=float_unpack),
    Row('SNR_MAX', 4, '.2f', parser=float_unpack),
    Row('CRC16', 2),
    Row('SIZE', 2),
    Row('PAYLOAD', 0, 'X'),
], 'little')


exp_payload: list[Row] = [
    Row('DEV_ID', 1),
    Row('MODEM_ID', 1),
    Row('IF_CHAN', 1),
    Row('RESERVE', 3, 'X'),
    Row('COUNT_MS', 4),
    Row('RSSI_CHANNEL', 4, '.2f', parser=float_unpack),
    Row('RSSI_SIGNAL', 4, '.2f', parser=float_unpack),
    Row('SNR', 4, '.2f', parser=float_unpack),
    Row('SNR_MAX', 4, '.2f', parser=float_unpack),
    Row('SNR_MIN', 4, '.2f', parser=float_unpack),
]

exp_data_body: list[Row] = [
    Row('TIME_FRACTIONAL_MS', 2),
    Row('EXP_SEQ_NUM', 1),
    Row('TX_MSG_NUM', 1),
    Row('STEP_NUM', 2),
    Row('RESERVE', 2, 'X'),
    Row('MODULE', 1),
    *SubFrame(tx_params),
    Row('MSG_LEN', 1),
    Row('ACCOMP_INFO', 16, 'X', byte_order='big'),
    *SubFrame(exp_payload, postfix='_1'),
    *SubFrame(exp_payload, postfix='_2'),
    Row('RESERVE', 12, 'X'),
]

ID49: Frame = Frame('ID49', [
    *SubFrame(header),
    *SubFrame(exp_data_body),
    Row('CRC16', 2, 'X'),
], 'little')

EXP_DATA: Frame = Frame('EXP_DATA', [
    *SubFrame(header),
    *SubFrame(exp_data_body),
    Row('CRC16', 2, 'X'),
], 'little')

EXP_REPORT: Frame = Frame('EXP_REPORT', [
    *SubFrame(header),
    *SubFrame(exp_report_body),
    Row('CRC16', 2, 'X'),
], 'little')

ID33: Frame = ID17


unknown_frame = Frame('UndefinedFrame', [Row('UndefinedData', 0, 'X')])
marathon_frames: dict[int, Frame] = {0: ID0, 1: ID1, 4: ID4, 7: ID7, 17: ID17,
                                    20: ID20, 22: ID22, 33: ID33, 49: ID49}
marathon_frames_dict: dict[int, Frame] = {  i: marathon_frames.get(i, unknown_frame)
                                            for i in range(66)}


class IFrame(Frame):
    def __init__(self, frame_type: str, rows: list[Row], 
                 byte_order: Literal['big', 'little'] = 'little', 
                 use_frame_type_as_header: bool = True) -> None:
        new_rows = [*SubFrame(header), *rows, Row('CRC16', 2, 'X')]
        super().__init__(frame_type, new_rows, byte_order, use_frame_type_as_header)


if __name__ == '__main__':
    data: list[str] = ['F1 0F 00 00 10 10 00 00 26 00 00 00 00 00 01 01 00 00 00 00 01 07 0A 01 01 00 12 00 00 B8 82 2B 76 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE 78 EF',
                        'F1 0F 00 00 10 10 01 00 28 00 00 00 00 00 01 02 01 00 00 00 01 07 0A 01 01 00 12 00 00 B8 82 2B 76 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE 7B 8D',
                        'F1 0F 00 00 10 10 02 00 2A 00 00 00 00 00 01 03 02 00 00 00 03 07 0A 01 01 00 12 00 00 50 0B 9C 76 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 01 07 00 00 00 B3 1A 00 00 00 00 01 43 00 00 02 43 00 00 18 41 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE 6F 52',
                        'F1 0F 00 00 10 10 03 00 2C 00 00 00 00 00 01 04 03 00 00 00 03 07 0A 01 01 00 12 00 00 60 57 81 76 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 00 01 00 00 00 2B 2C 00 00 00 00 01 43 00 00 02 43 00 00 0C 41 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE EA A4',
                        'F1 0F 00 00 10 10 04 00 2E 00 00 00 00 00 01 05 04 00 00 00 05 07 0A 01 01 00 12 00 00 38 22 01 77 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 06 00 04 00 00 00 E5 33 00 00 00 00 06 43 00 00 07 43 00 00 1C 41 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE AB BD',
                        'F1 0F 00 00 10 10 05 00 30 00 00 00 00 00 01 06 05 00 00 00 05 07 0A 01 01 00 12 00 00 E8 93 0C 77 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 06 01 02 00 00 00 BB 3C 02 00 00 00 07 43 00 00 08 43 00 00 04 41 00 00 00 00 00 00 00 00 FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE FE F3 DA']
    blist: list[bytes] = [bytes.fromhex(d) for d in data]
    print(ID7.parse_table(blist, ['RESERVE', 'LABEL', 'ID_DEV'])['FRAME_NUM'].astype(int).to_list())