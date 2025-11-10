import snap7
import snap7.util as s7util
import time

# ---------------debug prog voor werking S7--------------------
#run deze code om de werking van de S7 communicatie te testen los van de rest van de simulator

ip = "192.168.0.1"
rack = 0
slot = 1

client = snap7.client.Client()
try:
    client.connect(ip, rack, slot, 102)
    if client.get_connected():
        print(" Verbonden met PLC")
    else:
        print(" Geen verbinding")
except Exception as e:
    print("Fout:", e)

buffer_AI = bytearray(32)
buffer_DI = bytearray(2)

def SetDI(byte: int, bit: int, value: int):    
    """
    Set a digital input (DI) bit in the PLC input process image (E/I area).

    byte: selects which input byte in the PLC is used, as defined by the GUI  
    bit: bit position (0–7) within the selected byte  
    value: True/False or 1/0 to set or clear the bit
    """
    if byte >= 0:
        if 7 >= bit >= 0:
            if value:  # if the value is > 0
                buffer_DI[0] |= (1 << bit)  # shift binary 1 by bit index, e.g. (1 << 3) = 00001000
            else:
                buffer_DI[0] &= ~(1 << bit)  # invert bit mask, e.g. ~(1 << 3) = 11110111
            client.eb_write(start=byte, size=1, data=buffer_DI)
            return int(bool(value))
    return -1


def GetDO(byte: int, bit: int):
    """
    Read a digital output (DO) bit from the PLC output process image (A/Q area).

    byte: selects which output byte in the PLC is used, as defined by the GUI  
    bit: bit position (0–7) within the selected byte
    """
    if byte >= 0:
        if 7 >= bit >= 0:
            data = client.ab_read(byte, 1)
            return int(s7util.get_bool(data, 0, bit))
    return -1


def SetAI(byte: int, value: int):
    """
    Set an analog input (AI) value as a 16-bit UNSIGNED INTEGER (0–65535) in the PLC input process image (E/I area).

    byte: selects which input byte in the PLC is used, as defined by the GUI  
    value: 0–65535 (word)
    """
    if byte >= 0:
        if 0 <= value <= 65535:
            lowByte = value & 0xFF  # 0xFF = mask for one byte (0b11111111)
            highByte = (value >> 8) & 0xFF
            buffer_AI[0] = highByte
            buffer_AI[1] = lowByte
            client.eb_write(start=byte, size=2, data=buffer_AI)
            return int(value)
        return -1
    return -1


def GetAO(byte: int):
    """
    Read an analog output (AO) value as a 16-bit SIGNED INTEGER (-32768–32767) from the PLC output process image (A/Q area).

    byte: selects which output byte in the PLC is used, as defined by the GUI
    """
    if byte >= 0:
        data = client.ab_read(start=byte, size=2)
        return s7util.get_int(data, 0)
    return -1

def print_status():
    # Digitale ingangen
    di_vals = []
    for byte in range(len(buffer_DI)):
        data = client.eb_read(start=byte, size=1)
        for bit in range(8):
            di_vals.append(f"{byte}.{bit}:{(data[0] >> bit) & 1}")
    
    # Digitale uitgangen
    do_vals = []
    for byte in range(len(buffer_DI)):
        for bit in range(8):
            do_vals.append(f"{byte}.{bit}:{GetDO(byte, bit)}")
    
    # Analoge ingangen (lees 2 bytes per AI)
    ai_vals = []
    for byte in range(2, len(buffer_AI)+2, 2):
        data = client.eb_read(start=byte, size=2)
        val = (data[0] << 8) | data[1]
        ai_vals.append(f"{byte}:{val}")
    
    # Analoge uitgangen
    ao_vals = []
    for byte in range(2, 34, 2):
        ao_vals.append(f"{byte}:{GetAO(byte)}")
    
    print(f"DI: {' '.join(di_vals)}")
    print(f"DO: {' '.join(do_vals)}")
    print(f"AI: {' '.join(ai_vals)}")
    print(f"AO: {' '.join(ao_vals)}")
    print('-'*80)

while True:
    SetDI(0,0,1)
    SetDI(1,4,1)  
    SetDI(0,5,1) 
    SetDI(1,5,1)

    SetAI(2,0)
    SetAI(4,255)
    SetAI(6,-25000)
    SetAI(20,69)
    SetAI(32,69)
    print_status()

    time.sleep(1)