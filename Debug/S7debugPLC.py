import snap7
import snap7.util as s7util
import time

# ---------------debug prog voor werking S7--------------------

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
    # Digitale ingangen (2 bytes)
    di_str = ' '.join(f"{b}.{bit}:{(buffer_DI[b] >> bit) & 1}" 
                      for b in range(len(buffer_DI)) for bit in range(8))
    
    # Digitale uitgangen (2 bytes)
    do_str = ' '.join(f"{b}.{bit}:{GetDO(b, bit)}" 
                      for b in range(len(buffer_DI)) for bit in range(8))
    
    # Analoge ingangen (16 waarden, 2 bytes elk)
    ai_str = ' '.join(f"{i}:{(buffer_AI[i*2]<<8) | buffer_AI[i*2+1]}" 
                      for i in range(16))
    
    # Analoge uitgangen (16 waarden, 2 bytes elk)
    ao_str = ' '.join(f"{i}:{GetAO(i*2)}" 
                      for i in range(16))
    
    print(f"DI: {di_str}")
    print(f"DO: {do_str}")
    print(f"AI: {ai_str}")
    print(f"AO: {ao_str}")
    print('-'*80)




while True:
    SetDI(0,0,1)
    SetDI(1,4,1)  
    SetDI(0,5,1) 
    SetDI(1,5,1)

    GetDO(0,1)
    GetDO(0,5)
    GetDO(1,7)  

    SetAI(2,255)
    SetAI(4,255)
    SetAI(6,-25000)
    SetAI(20,69)
    SetAI(32,69)

    print(GetAO(2))
    GetAO(4)
    GetAO(6)
    GetAO(8)
    print(GetAO(32))
    print_status()
    time.sleep(1)