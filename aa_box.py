from sx127x_gs.radio_controller import RadioController

"""        
    self.modulation: SX127x_Modulation = kwargs.get('modulation', SX127x_Modulation.LORA)
    self.coding_rate: SX127x_CR = kwargs.get('ecr', self.cr.CR5)  # error coding rate
    self.bandwidth: SX127x_BW = kwargs.get('bw', self.bw.BW250)  # bandwidth  BW250
    self.spread_factor: int = kwargs.get('sf', 10)  # spreading factor  SF10
    self.frequency: int = kwargs.get('frequency', 436_500_000)   # 436700000
    self.crc_mode: bool = kwargs.get('crc_mode', True)  # check crc
    self.tx_power: int = kwargs.get('tx_power', 17)  # dBm
    self.sync_word: int = kwargs.get('sync_word', 0x12)
    self.preamble_length: int = kwargs.get('preamble_length', 8)
    self.auto_gain_control: bool = kwargs.get('agc', True)  # auto gain control
    self.payload_length: int = kwargs.get('payload_size', 10)  # for implicit mode
    self.low_noize_amplifier: int = kwargs.get('low_noize_amplifier', 5)  # 1 - min; 6 - max
    self.lna_boost: bool = kwargs.get('lna_boost', False)  # 150% LNA current
    self.header_mode: SX127x_HeaderMode = kwargs.get('header_mode', SX127x_HeaderMode.EXPLICIT) # fixed payload size
    self.low_data_rate_optimize: bool = kwargs.get('low_data_rate_optimize', True)
"""

radio = RadioController(interface="Serial")
if radio.connect('COM32'):
    radio.user_cli()