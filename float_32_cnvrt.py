
def convert_to_float32(var, byteorder = 'little'):
    initial_var = var
    print(f"initial_var = {initial_var} = 0x{initial_var:08X}")
    if byteorder == 'little':
        pass
    else:
        initial_var_bytes = initial_var.to_bytes(4, byteorder="little")
        initial_var = int.from_bytes(initial_var_bytes, byteorder=byteorder)
        print(f"initial_var with reverted bytes (big endian) = {initial_var} = 0x{initial_var:08X}")

    man = initial_var  & 0x7FFFFF
    exp = (initial_var >> 23) & 0xFF
    sign = (initial_var >> 31) & 0x1

    base_man = (man | (1 << 23)) / 0x7FFFFF

    result  = (-1**sign)*(2**(exp-127))*(base_man)

    print(f"{exp=}, {man=}, {sign=}")
    print(f"{base_man=}")
    print(f"{result=}")
    return result

if __name__ == "__main__":
    var_dict = {
        "rssi ch": 1124204544,
        "rssi si": 1124204544,
        "snr": 3239051264,
    }
    for key, item in var_dict.items():
        print(f"\nThe value name is <{key}>")
        convert_to_float32(item)

