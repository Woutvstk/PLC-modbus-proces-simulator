import snap7
import time


logo = snap7.logo.Logo()

### <ip_address, tsap_snap7 (client) 03.00 = 0x0300, tsap_logo (server) 20.00 = 0x2000>
logo.connect("192.168.0.2", 0x0300, 0x2000)
if logo.get_connected():
    print(f"Connected to LOGO")
else:
    print(f"Cannot connect to LOGO")

def isConnected() -> bool:
    return logo.get_connected()

def SetDI( byte: int, bit: int, value: bool):
    """
    Sets a digital input (DI) via byte and bit.
    byte: 0..n  | bit: 0..7

    example:
    i1 = byte:0 bit :0 // i10 = byte:1 bit :1,..."""

    if 0 <= bit < 8:
        address = f"V{byte+1024}.{bit}"
        logo.write(address, int(bool(value)))
        return int(bool(value))
    return 0

def GetDO( byte: int, bit: int):
    """
    Lees een digitale output (DO) via byte en bit.
    byte: 0..n  | bit: 0..7
    example:
    q1 = byte:0 bit :0 // q10 = byte:1 bit :1,...
    """
    if 0 <= bit < 8:
        address = f"V{byte+1064}.{bit}"
        data = logo.read(address)
        return int(bool(data))
    return 0

def SetAI(self, byte: int, value: int):
    """
    Zet een analoge input (AI) via byte."""
    if byte  >= 0:
        val = int(value) & 0xFFFF
        address = f"VW{byte+1032}"
        logo.write(address, val)
        return val
    return 0

def GetAO( byte: int):
    """
    Lees een analoge output (AO) via byte.
    Elke AO = 2 bytes => byte moet even zijn.
    """
    if byte % 2 == 0:
        address = f"VW{byte+1072}"
        data = logo.read(address)
        return int(data)
    return 0

def reset_registers():
    """Reset alle V geheugen naar 0"""
    for byte in range(1024, 1468):
            logo.write(f"VW{byte}", 0)

def print_status():
    """Compact overzicht van 16 DI, DO, AI en AO"""
    di_values = [1 if i % 2 == 0 else 0 for i in range(16)]  # (dummy DI-waarden)
    do_values = [GetDO(i // 8, i % 8) for i in range(16)]
    ai_values = [i * 500 for i in range(16)]  # (dummy AI’s)
    ao_values = [GetAO(i * 2) for i in range(16)]

    print("------------------------------------------------------------")
    print(" DI:", " ".join(f"{v:1}" for v in di_values))
    print(" DO:", " ".join(f"{v:1}" for v in do_values))
    print(" AI:", " ".join(f"{v:5}" for v in ai_values))
    print(" AO:", " ".join(f"{v:5}" for v in ao_values))
    print("------------------------------------------------------------\n")   

while True:
    SetDI(0,0,1)
    SetDI(1,1,1) #i10
    SetDI(0,4,1) #i5
    SetDI(0,5,1) #i6

    GetDO(0,1)
    GetDO(0,5)
    GetDO(1,7)  

    SetAI(2,255)
    SetAI(4,255)
    SetAI(6,-25000)
    SetAI(8,69)
    SetAI(10,69)

    GetAO(0)
    GetAO(2)
    GetAO(4)
    GetAO(6)
    
    print_status()
    time.sleep(1)
