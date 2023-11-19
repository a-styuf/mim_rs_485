import time

class Tx_Data:
    def __init__(self, **kw):
        self.module = kw.get("module", 0x01)
        #
        self.bw = kw.get("bw", 8) 	                # ISM : 6..9                   
        self.sf = kw.get("sf", 10)  		        # ISM : 6..12                  
        self.cr = kw.get("cr", 1)  		            # ISM : 1..4 : 4/5..4/8        
        self.crc_ = kw.get("crc", 1)  	            # ISM : 0 or 1                 
        self.ldr = kw.get("ldr", 1) 		        # ISM : 0 or 1                 
        self.sync = kw.get("sync", 0x12)            # ISM : e.g.  0x12             
        self.r_freq = kw.get("r_freq", 868_000_000)  	# ISM : 861000000..1020000000  
        self.f_pwr = kw.get("f_pwr", 0)              # ISM : 0..15 : min..max
        #
        self.packet_type    = 0x02
        self.packet_size    = 0x00
        self.n_immediate    = 0x00
        self.time_stamp     = 0x00
        #
        self.pay_load       = b""
        
    def form_packet(self):
        #
        packet = b""
        # 
        packet += int.to_bytes(self.packet_type, 2, byteorder="little", signed=False)
        self.packet_size = 32 + len(self.pay_load)
        packet += int.to_bytes(self.packet_size, 2, byteorder="little", signed=False)
        packet += int.to_bytes(self.module, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.n_immediate, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.time_stamp, 8, byteorder="little", signed=False)
        #
        packet += int.to_bytes(self.bw, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.sf, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.cr, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.crc_, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.ldr, 1, byteorder="little", signed=False)
        packet += int.to_bytes(self.sync, 1, byteorder="little", signed=False)
        
        packet += int.to_bytes(0x0000, 2, byteorder="little", signed=False)
        
        packet += int.to_bytes(self.r_freq, 4, byteorder="little", signed=False)
        packet += int.to_bytes(self.f_pwr, 1, byteorder="little", signed=False)
        
        packet += int.to_bytes(0x000000, 3, byteorder="little", signed=False)
        
        
        packet += int.to_bytes(len(self.pay_load), 1, byteorder="little", signed=False)
        packet += bytes(self.pay_load)
        # print(packet.hex(" "), "\n",  self.pay_load.hex(" "))
        return packet
    
    def set_pay_load(self, pay_load=b""):
        if pay_load:
            if len(pay_load) <= 256:
                self.pay_load = pay_load
            else:
                raise(ValueError, f"pay_load too long: expected length less or equal then 256, real length is {len(pay_load)}")
        else:
            raise(ValueError, f"pay_load is absent")