from processSim.tankSim import tankSim
from plcCom.plcModBusTCP import plcModBusTCP
from plcCom.plcS7 import plcS7
import time

"""Initialize process0 object"""

process0 = tankSim("process0", 2000, 250, 135)

Protocol = "S7"   # of "ModBusTCP"

if Protocol == "ModBusTCP":
    PlcCom = plcModBusTCP("192.168.111.80", 502)
elif Protocol == "S7":
    PlcCom = plcS7("192.168.111.80", 0, 1)

PlcCom.connect()

# remember at what time we started
startTime = time.time()


while True:

    # print out the current time since start and the current liquid level
    print(
    '''Examples of using the plcCom class'''

        process0.valveInOpen = True
        process0.valveOutOpen = False

    # during 10 to 20 seconds: let liquid flow out of the tank
    elif (10 < (time.time() - startTime) < 20):
        process0.valveInOpen = False
        process0.valveOutOpen = True
    print("Setting analog inputs...")
    PlcCom.SetAI(0, 12345)  # Set AI0 (register 16) to 12345
    PlcCom.SetAI(15, 30000)  # Set AI15 (register 17) to 30000

    #  Read digital outputs (DO)
    print("Reading digital outputs...")
    do0 = PlcCom.GetDO(0)
    do1 = PlcCom.GetDO(1)

    #  Read analog outputs (AO)
    print("Reading analog outputs...")
    ao0 = PlcCom.GetAO(0)
    ao1 = PlcCom.GetAO(1)

    time.sleep(1.5)
