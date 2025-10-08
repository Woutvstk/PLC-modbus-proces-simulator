from processSim.tankSim import tankSim
from plcCom.plcModBusTCP import plcModBusTCP
from plcCom.plcS7 import plcS7
import time

"""Initialize process0 object"""


Protocol = "S7"   # of "ModBusTCP"

if Protocol == "ModBusTCP":
    PlcCom = plcModBusTCP("192.168.111.80", 502)
elif Protocol == "S7":
    PlcCom = plcS7("192.168.111.80", 0, 1)

PlcCom.connect()


while True:

    '''Examples of using the plcCom class'''

    # 3️Set some digital inputs
    print("Setting digital inputs...")
    PlcCom.SetDI(0, 1)  # Set DI0 to 1 (ON)
    PlcCom.SetDI(1, 0)  # Set DI1 to 0 (OFF)

    # Set some analog inputs
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
