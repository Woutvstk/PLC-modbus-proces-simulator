from processSim.tankSim import tankSim
from plcCom.plcModBusTCP import plcModBusTCP
from plcCom.plcS7 import plcS7
import time

"""Initialize process0 object"""

process0 = tankSim("process0", 2000, 250, 135)
process0.simStart()

""""Initialize plc communication object"""

if "Protocol" == "ModBusTCP":
    PlcCom = plcModBusTCP("192.168.111.80", 502)
elif "Protocol" == "S7" or True == True:
    # IP address, rack, slot (from HW settings)
    PlcCom = plcS7("192.168.111.80", 0, 1)

PlcCom.connect()
PlcCom.reset_registers()

DI = [0]*16
DO = [0]*16
AI = [0]*16
AO = [0]*16


# remember at what time we started
startTime = time.time()


while True:

    # print out the current time since start and the current liquid level
    print(
        f"At time: {int(time.time() - startTime)}, Current liquid level: {int(process0.liquidVolume)}")

    # only print out status every second
    time.sleep(1)

    # during the first 10 seconds: let liquid flow in the tank
    if ((time.time() - startTime) < 10):
        process0.valveInOpen = True
        process0.valveOutOpen = False

    # during 10 to 20 seconds: let liquid flow out of the tank
    elif (10 < (time.time() - startTime) < 20):
        process0.valveInOpen = False
        process0.valveOutOpen = True

    # after 20 close both valves
    else:
        process0.valveInOpen = False
        process0.valveOutOpen = False

    for i in range(16):
        DI[i] = PlcCom.SetDI(i, 1)
        AI[i] = PlcCom.SetAI(i, 1)
        DO[i] = PlcCom.GetDO(i)
        AO[i] = PlcCom.GetAO(i)

    # Debug
    print(f"DI={list(DI)}")
    print(f"DO={list(DO)}")
    print(f"AI={list(AI)}")
    print(f"AO={list(AO)}")
    print("-"*50)
