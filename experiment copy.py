from mim import MimRS485Device
import time
from threading import Thread, Lock
from transaction_list import *
from loguru import logger
from sx127x_gs.radio_controller import RadioController
import pandas as pd
from loguru import logger

class Experiment:
    def __init__(self, **kw) -> None:
        self.mim: MimRS485Device = kw.get("mim", None)
        self.parsing: bool = kw.get("parsing", True)
        pass
    
    def _transaction(self, addr=0x0C, id=0x05, mode="cmd", data=b"") -> None:
        tx_frame: bytes = self.mim.request(addr=addr, id=id, mode=mode, data=data)
        logger.info(f"TX: {tx_frame.hex(" ")}") 
        #
        while self.mim.ready_to_transaction is False:
                time.sleep(0.001)
        #
        rx_frame: bytes = self.mim.get_last_data()
        logger.info(f"RX: {rx_frame.hex(" ")}") 
        if rx_frame:
            if (self.mim.check_frame(fr=rx_frame) >= 0):
                if self.parsing is True:
                    logger.info(f"{(self.mim.parc_data(rx_frame))}") 
        pass
    
    
    def set_start_wr_settings(self, step_num:int = 60, period_s: int = 2, start_block: int = 0, data_len: int= 16, frame_cnter_to_save:int = 1):
        settings_b: bytes = 0xABCD.to_bytes(2, byteorder='little')
        settings_b += 0x00.to_bytes(2, byteorder='little')
        settings_b += step_num.to_bytes(2, byteorder='little')
        settings_b += period_s.to_bytes(2, byteorder='little')
        settings_b += start_block .to_bytes(4, byteorder='little')
        settings_b += data_len.to_bytes(1, byteorder='little')
        settings_b += frame_cnter_to_save.to_bytes(1, byteorder='little')
        self._transaction(addr = 0x0C, id = 5, mode="cmd", data=settings_b)
        pass
    
    def set_tx_msg(self, num:int=0, m_num:int=1, BW=6, SF=6, CR=1, CRC_=0, LDR=0, Sync=0x12, InvertIQ=0, RFreq=861000000, FPwr=0, PwrNoOn=0, Pleng=4):
        tx_msg: bytes = 0xABCD.to_bytes(2, byteorder='little')
        tx_msg += 0x01.to_bytes(2, byteorder='little')
        tx_msg += num.to_bytes(1, byteorder='little')
        tx_msg += m_num.to_bytes(1, byteorder='little')
        tx_msg += BW.to_bytes(1, byteorder='little')
        tx_msg += SF.to_bytes(1, byteorder='little')
        tx_msg += CR.to_bytes(1, byteorder='little')
        tx_msg += CRC_.to_bytes(1, byteorder='little')
        tx_msg += LDR.to_bytes(1, byteorder='little')
        tx_msg += Sync.to_bytes(1, byteorder='little')
        tx_msg += InvertIQ.to_bytes(1, byteorder='little')
        tx_msg += 0xFE.to_bytes(1, byteorder='little')
        tx_msg += RFreq.to_bytes(4, byteorder='little')
        tx_msg += FPwr.to_bytes(1, byteorder='little')
        tx_msg += PwrNoOn.to_bytes(1, byteorder='little')
        tx_msg += 0xFEFE.to_bytes(2, byteorder='little')
        tx_msg += Pleng.to_bytes(1, byteorder='little')
        self._transaction(addr = 0x0C, id = 5, mode="cmd", data=tx_msg)
        pass
    
    def tx_data(self, m_num:int=1, BW=6, SF=6, CR=1, CRC_=0, LDR=0, Sync=0x12, InvertIQ=0, RFreq=861000000, FPwr=0, PwrNoOn=0, data=b""):
        size: int = 31 + len(data)
        Pleng: int = len(data)
        #
        tx_msg: bytes = 0x03.to_bytes(2, byteorder='little')
        tx_msg += size.to_bytes(2, byteorder='little')
        tx_msg += m_num.to_bytes(1, byteorder='little')
        tx_msg += 0x00.to_bytes(1, byteorder='little')
        tx_msg += 0x00.to_bytes(8, byteorder='little')
        tx_msg += BW.to_bytes(1, byteorder='little')
        tx_msg += SF.to_bytes(1, byteorder='little')
        tx_msg += CR.to_bytes(1, byteorder='little')
        tx_msg += CRC_.to_bytes(1, byteorder='little')
        tx_msg += LDR.to_bytes(1, byteorder='little')
        tx_msg += Sync.to_bytes(1, byteorder='little')
        tx_msg += InvertIQ.to_bytes(1, byteorder='little')
        tx_msg += 0xFE.to_bytes(1, byteorder='little')
        tx_msg += RFreq.to_bytes(4, byteorder='little')
        tx_msg += FPwr.to_bytes(1, byteorder='little')
        tx_msg += PwrNoOn.to_bytes(1, byteorder='little')
        tx_msg += 0xFEFE.to_bytes(2, byteorder='little')
        tx_msg += Pleng.to_bytes(1, byteorder='little')
        tx_msg += data
        self._transaction(addr = 0x0C, id = 18, mode="cmd", data=tx_msg)
        pass
    
    def start(self):
        mim_cmd_b: bytes = 0xABBC.to_bytes(2, byteorder='little')
        mim_cmd_b += 0x00.to_bytes(2, byteorder='little')
        mim_cmd_b += 0x01.to_bytes(2, byteorder='little')
        self._transaction(addr = 0x0C, id = 3, mode="cmd", data=mim_cmd_b)
        pass
    
    def stop(self):
        mim_cmd_b: bytes = 0xABBC.to_bytes(2, byteorder='little')
        mim_cmd_b += 0x00.to_bytes(2, byteorder='little')
        mim_cmd_b += 0x00.to_bytes(2, byteorder='little')
        self._transaction(addr = 0x0C, id = 3, mode="cmd", data=mim_cmd_b)
        pass
    
    def read_tmi(self):
        self._transaction(addr = 0x0C, id = 7, mode="data", data=b"")
        pass
    
    def set_start_rd_block(self, block:int=0):
        exp_rd_page_set_b: bytes = 0xABEF.to_bytes(2, byteorder='little')
        exp_rd_page_set_b += block.to_bytes(4, byteorder='little')
        self._transaction(addr = 0x0C, id = 48, mode="cmd", data=exp_rd_page_set_b)
        pass
    
    def read_mem_frame(self):
        self._transaction(addr = 0x0C, id = 49, mode="data", data=b"")
        pass
    
    def set_radio_module_to_default(self):
        for num in range(1, 14):
            def_cmd_b: bytes = 0xABBC.to_bytes(2, byteorder='little')
            def_cmd_b += 0x02.to_bytes(2, byteorder='little')
            def_cmd_b += num.to_bytes(2, byteorder='little')
            self._transaction(addr = 0x0C, id = 3, mode="cmd", data=def_cmd_b)
            time.sleep(0.1)
        pass
    
if __name__ == "__main__":
    logger.add("logs/{time}_experiment.log")
    #
    start_time: float = time.perf_counter()
    logger.info(" Начало эксперимента с Модуль IoT")
    #
    #mim= mim.MimRS485Device(alias="MA", addr=0x01, serial_numbers=["A50285"], debug=False)
    mim = MimRS485Device(alias="MFR", addr=0x02, port="COM50", debug=False)
    mim.open_port()
    # mim.debug = False
    #
    exp = Experiment(mim=mim)
    #
    time.sleep(1)
    exp.stop()
    time.sleep(1)
    step_num = 129
    period_s = 1
    start_block = 0
    frame_cnter_to_save = 1
    exp.set_start_wr_settings(step_num=step_num, period_s=period_s, start_block=start_block, data_len=16, frame_cnter_to_save=frame_cnter_to_save)
    #
    freq_list: list[int] = [    868000000, 863275000, 863450000, 863625000,\
                                863800000, 863975000, 864325000, 864500000]
    module_list: list[int] = [  9, 9, 9, 9,\
                                9, 9, 9, 9]
    for num in range(8):    
        time.sleep(0.1)
        exp.set_tx_msg(num=num, m_num=module_list[num], BW=7, SF=10, CR=1, CRC_=1, 
                                                        LDR=0, Sync=0x12, InvertIQ=0, RFreq=freq_list[num], 
                                                        FPwr=1, PwrNoOn=0, Pleng=4)
    #
    time.sleep(0.1)
    exp.set_radio_module_to_default()
    #
    time.sleep(1)
    exp.start()
    #
    experiment_time: int = (period_s*step_num*2) + 1 + 1 + 1 + 10
    tmi_interval_s = 10
    for i in range(experiment_time//tmi_interval_s):
        time.sleep(tmi_interval_s)
        exp.read_tmi()
    #
    time.sleep(1)
    exp.set_start_rd_block(block = start_block)
    time.sleep(1)
    for i in range(5+step_num*frame_cnter_to_save):
        exp.read_mem_frame()
        time.sleep(0.1)
    #
    logger.info(f"Эксперимент окончен за {(time.perf_counter() - start_time):.3f}")
    