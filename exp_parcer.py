from genericpath import exists
import re
import os
import time
import configparser
import datetime
from loguru import logger
import mim_parser
from pandas import DataFrame
import pandas as pd
from pathlib import Path


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

file_name = "logs\\2024-10-11_12-18-41_497815.log"

time_start: float = time.perf_counter()

exp_rx_frame_pattern: re.Pattern = re.compile(r"([fF]1 0[fF] [0-9a-fA-F]{2} [0-9a-fA-F]{2} 10 [0-9a-fA-F]{2} ([0-9a-fA-F]{2}[ ]{0,1}){122})")
exp_report_frame_pattern: re.Pattern = re.compile(r"([fF]1 0[fF] [0-9a-fA-F]{2} [0-9a-fA-F]{2} 11 [0-9a-fA-F]{2} ([0-9a-fA-F]{2}[ ]{0,1}){122})")

def find_exp_rx_data_frames(data_str=""):
    
    pass
    
if __name__ == '__main__':
    # если папки нет, то создаем папку для выходных данных
    try:
        os.mkdir("Data")
    except:  # noqa: E722
        pass
    #
    logger.add("data_parsing_logs/{time}_exp_pars.log")
    #
    with open(file_name, "r") as f:
        exp_data_str: str = f.read()
        pass 
    #
    rx_frame_result: list = exp_rx_frame_pattern.findall(exp_data_str)
    logger.info(f"<{len(rx_frame_result)} frames found>")
    rx_report_result: list = exp_report_frame_pattern.findall(exp_data_str)
    logger.info(f"<{len(rx_report_result)} reports found>")
    #
    rx_data_frames: list[bytes] = []
    for result in rx_frame_result:
        rx_data_frames.append(bytes.fromhex(result[0]))
    #
    logger.info(f"First frame {rx_data_frames[0].hex(" ")}")
    logger.info(f"Last frame {rx_data_frames[-1].hex(" ")}")
    #
    report_df: DataFrame = mim_parser.EXP_DATA.parse_table(rx_data_frames, drop_columns=['RESERVE', 'RESERVE_1', 'RESERVE_2'])
    # rx_data_df: DataFrame | None = griffin_parser(bytes.fromhex(pl_spu_tmi))
    logger.info(report_df)
    logger.info(report_df.columns)
    rx_data_1_columns: list[str] = ['FR_TIME', 'TIME_FRACTIONAL_MS',  'EXP_SEQ_NUM',
                                    'TX_MSG_NUM', 'STEP_NUM', 'MODULE', 'BW', 'SF', 'CR',
                                    'CRC_EN', 'LDRO', 'SYNC', 'IQ_INVERT', 'FREQUENCY', 'TX_POWER',
                                    'DISABLE_AMPL', 'MSG_LEN', 'ACCOMP_INFO', 'DEV_ID_1', 'MODEM_ID_1',
                                    'IF_CHAN_1', 'COUNT_MS_1', 'RSSI_CHANNEL_1', 'RSSI_SIGNAL_1', 'SNR_1',
                                    'SNR_MAX_1', 'SNR_MIN_1']
    rx_data_2_columns: list[str] = ['FR_TIME', 'TIME_FRACTIONAL_MS',  'EXP_SEQ_NUM',
                                    'TX_MSG_NUM', 'STEP_NUM', 'MODULE', 'BW', 'SF', 'CR',
                                    'CRC_EN', 'LDRO', 'SYNC', 'IQ_INVERT', 'FREQUENCY', 'TX_POWER',
                                    'DISABLE_AMPL', 'MSG_LEN', 'ACCOMP_INFO', 'DEV_ID_1', 'MODEM_ID_2',
                                    'IF_CHAN_2', 'COUNT_MS_2', 'RSSI_CHANNEL_2', 'RSSI_SIGNAL_2', 'SNR_2',
                                    'SNR_MAX_2', 'SNR_MIN_2']
    rx_data_columns: list[str] = ['FR_TIME', 'TIME_FRACTIONAL_MS',  'EXP_SEQ_NUM',
                                    'TX_MSG_NUM', 'STEP_NUM', 'MODULE', 'BW', 'SF', 'CR',
                                    'CRC_EN', 'LDRO', 'SYNC', 'IQ_INVERT', 'FREQUENCY', 'TX_POWER',
                                    'DISABLE_AMPL', 'MSG_LEN', 'ACCOMP_INFO', 'DEV_ID', 'MODEM_ID',
                                    'IF_CHAN', 'COUNT_MS', 'RSSI_CHANNEL', 'RSSI_SIGNAL', 'SNR',
                                    'SNR_MAX', 'SNR_MIN']
    rx_data_1_df: DataFrame = report_df[rx_data_1_columns]
    rx_data_2_df: DataFrame = report_df[rx_data_2_columns]
    # logger.info(f"{rx_data_1_df}, {rx_data_2_df}")
    #
    rx_data_1_df.columns = rx_data_columns
    rx_data_2_df.columns = rx_data_columns
    # logger.info(f"{rx_data_1_df}, {rx_data_2_df}")
    #
    rx_data_df: DataFrame = pd.concat([rx_data_1_df, rx_data_2_df], ignore_index=True, axis=0)
    logger.info(f"rx_data_df\n{rx_data_df}")
    # деление по типам отправленных сообщений
    message_box: list = [DataFrame() for i in range(16)]
    for index, row in rx_data_df.iterrows():
        # logger.info(f"{index}, {type(row)}, {row}, {row['TX_MSG_NUM']}")
        if(row["DEV_ID"] == "254"):
            pass
        else:
            msg_num: int = int(row['TX_MSG_NUM'])
            if 0 <= msg_num < 16:
                message_box[msg_num] = pd.concat([message_box[msg_num], row.to_frame().T], ignore_index=True)
            else:
                pass
            pass
    message_box_info: list = [df.shape[0] for df in message_box]
    logger.info(f"message_box_info = {message_box_info}")
    # деление по уникальному номеру принятого канала uniq_rx_num
    rx_module, rx_gate_way, rx_channel_num = 13, 4, 8
    full_channel_num = rx_module*rx_gate_way*rx_channel_num
    rx_channel_box: list = [DataFrame() for i in range(full_channel_num)]
    for df in message_box:
        for index, row in df.iterrows():
            uniq_ch_id: int = (int(row['DEV_ID']) * rx_channel_num * rx_gate_way) + (int(row['MODEM_ID']) * rx_channel_num) + int(row['IF_CHAN'])
            if uniq_ch_id < full_channel_num:
                rx_channel_box[uniq_ch_id] = pd.concat([rx_channel_box[uniq_ch_id], row.to_frame().T], ignore_index=True)
            pass
    pass
    rx_channel_box_info: list = [df.shape[0] for df in rx_channel_box]
    logger.info(f"rx_channel_info = {rx_channel_box_info}")
    #
    for index, df in enumerate(rx_channel_box):
        if df.shape[0] != 0:
            dir_name: str = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
            file_name: str = dir_name + f"_Experiment_data_Ch_{index}"
            #
            Path(f"Exp_csv_result\\{dir_name}").mkdir(parents=True, exist_ok=True)
            df.to_csv(f"Exp_csv_result\\{dir_name}\\{file_name}.csv")
    