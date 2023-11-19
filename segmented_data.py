
from crc import Calculator, Crc8, Configuration

label = 0xCDDE
id_data_len = 56
crc_init_val = 0xCD

class Segmented_Data_Frame:
    def __init__(self, **kw):
        #
        self.label = 0xCDDE
        self.seq_num = kw.get('seq_num', 0x00)
        self.segm_vol = kw.get('segm_vol', 1)
        self.segm_num = kw.get('segm_num', 0)
        self.data = kw.get('data', [0xFE])
        self.data_len = len(self.data)
        self.data.extend([0x00 for val in range(id_data_len-len(self.data))])
        #
        config = Configuration(
            width=8,
            polynomial=0x07,
            init_value=crc_init_val,
            final_xor_value=0x00,
            reverse_input=False,
            reverse_output=False,
        )
        self.crc_calculator = Calculator(config)
        #
        self.row_data = b""
        self.row_data += int.to_bytes(self.label,       2, byteorder="little", signed=False)
        self.row_data += int.to_bytes(self.seq_num,     2, byteorder="little", signed=False)
        self.row_data += int.to_bytes(self.segm_vol,    1, byteorder="little", signed=False)
        self.row_data += int.to_bytes(self.segm_num,    1, byteorder="little", signed=False)
        self.row_data += int.to_bytes(self.data_len,    1, byteorder="little", signed=False)
        self.row_data += bytes(self.data)
        #
        self.crc8 = self.crc_calculator.checksum(bytes(self.row_data))
        self.row_data += int.to_bytes(self.crc8,    1, byteorder="little", signed=False)


def segmented_data_data_list(id=65, seq_num=0, data=[]):
    data_list = []
    
    data_len = len(data)
    step = 0
    while(step < (data_len//id_data_len) + 1):
        frame_data = data[step*id_data_len : (min((step+1)*id_data_len, data_len))]
        frame = Segmented_Data_Frame(seq_num = seq_num, segm_vol = (data_len//id_data_len) + 1, segm_num = step, data=frame_data)
        data_list.append(frame.row_data)
        step += 1
    return data_list
