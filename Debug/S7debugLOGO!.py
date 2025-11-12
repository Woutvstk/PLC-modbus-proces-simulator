import snap7
import time

# ------------------ LOGO/S7 Setup ------------------
logo = snap7.logo.Logo()
logo.connect("192.168.0.2", 0x0300, 0x0200)

if logo.get_connected():
    print("Connected to LOGO")
else:
    print("Cannot connect to LOGO")


# ------------------ Functies ------------------
def isConnected() -> bool:
    return logo.get_connected()


def SetDI(byte: int, bit: int, value: bool):
    """Zet een digitale input (DI) via byte/bit
    byte: 0..n  | bit: 0..7
    example:
    <I1 = byte:0 bit :0 // I10 = byte:1 bit :1,...
    """
    if 0 <= bit < 8:
        address = f"V{byte}.{bit}"
        logo.write(address,int(bool(value)))
        return int(bool(value))
    return 0


def GetDO(byte: int, bit: int):
    """Lees digitale output (DO) via byte/bit"""
    if 0 <= bit < 8:
        address = f"V{byte + 1024}.{bit}"
        data = logo.read(address)
        return int(bool(data))
    return 0


def SetAI(byte: int, value: int):
    """Zet analoge input (AI) via byte"""
    if byte >= 0:
        val = int(value) & 0xFFFF
        address = f"VW{byte}"
        logo.write(address, val)
        return val
    return 0


def GetAO(byte: int):
    """Lees analoge output (AO) via byte"""
    if byte % 2 == 0:
        address = f"VW{byte+1072}"
        data = logo.read(address)
        return int(data)
    return 0


def reset_registers():
    """Reset alle V geheugen naar 0"""
    #for byte in range(1024, 1468):
        #logo.write(f"VW{byte}", 0)


def print_status():
    """Compact overzicht van 16 DI, DO, AI en AO"""
    # DI: lees 16 ingangen (dummy, kan vervangen worden met echte leesfunctie)
    #di_values = [1 if i % 2 == 0 else 0 for i in range(16)]
    # DO: lees 16 uitgangen
    do_values = [GetDO(i // 8, i % 8) for i in range(16)]
    # AI: dummy waarden of lees echte AI registers
   #ai_values = [SetAI(i * 2, i * 500) for i in range(16)]
    # AO: lees 16 analoge outputs
    #ao_values = [GetAO(i * 2) for i in range(16)]

    print("------------------------------------------------------------")
    #print(" DI:", " ".join(f"{v:1}" for v in di_values))
    print(" DO:", " ".join(f"{v:1}" for v in do_values))
   #print(" AI:", " ".join(f"{v:5}" for v in ai_values))
    #print(" AO:", " ".join(f"{v:5}" for v in ao_values))
    print("------------------------------------------------------------\n")


# ------------------ Main Loop ------------------
while True:
    # DI instellen
    SetDI(0, 0, 1)
    SetAI(2, 69)
    # DO uitlezen
    print( GetDO(0, 3))
   # print( GetDO(0, 1))

    # AI instellen

    # AO uitlezen

    # Status printen

    time.sleep(1)
    SetDI(0, 0, 1)

    time.sleep(1)
