import clr
import os
import time

#connects to to the softbus of a Siemens PLC simulator via an API DLL

# map van dit script
script_dir = os.path.dirname(os.path.abspath(__file__))

# pad naar DLL vanaf script_dir
dll_path = os.path.join(script_dir, "Siemens.Simatic.Simulation.Runtime.Api.x64.dll")

print(f"Trying to load DLL from: {dll_path}")
if not os.path.exists(dll_path):
    raise FileNotFoundError(f"DLL niet gevonden: {dll_path}")

# DLL importeren
clr.AddReference(dll_path)

from Siemens.Simatic.Simulation.Runtime import SimulationRuntimeManager #type: ignore

class plcSimAPI:

    """Class for communication with a Siemens S7 PLC simulator via Simatic.Simulation.Runtime API"""

    def __init__(self):
        """Initialize the PLC simulator manager"""
        self.manager = SimulationRuntimeManager()
        self.simulation_instance = None

    def connect(self, instance_name: str | None = None) -> bool:
        """Connect to the specified PLC simulation instance.
           Returns True if connected, False otherwise.
        """
        instances = self.manager.RegisteredInstanceInfo  # altijd up-to-date lijst

        if instance_name is not None:
            # Zoek specifieke instantie
            for inst in instances:
                if inst.Name == instance_name:
                    try:
                        self.simulation_instance = self.manager.CreateInterface(inst.Name)
                        print(f"Interface created for instance: {inst.Name}")
                        print(f"OperatingState: {self.simulation_instance.OperatingState}")
                        return True
                    except Exception as e:
                        print(f"Fout bij het maken van de interface voor {instance_name}: {e}")
                        return False
            print(f"Instantie '{instance_name}' niet gevonden.")
            return False

        else:
            # Geen naam opgegeven: probeer eerste beschikbare instantie
            print(f"{'-'*10} No instance defined, trying first available instance  {'-'*10}")
            for inst in instances:
                try:
                    self.simulation_instance = self.manager.CreateInterface(inst.Name)
                    if str(self.simulation_instance.OperatingState) == "Run":
                        print(f"{inst.Name} OperatingState = {self.simulation_instance.OperatingState}, connected successfully.")
                        return True
                    else:
                        print(f"{inst.Name} OperatingState = {self.simulation_instance.OperatingState}... trying next instance.") 
                except Exception:
                    continue
            print("No running instances found. Please check if a PLC simulator is running.")
            return False


    def isConnected(self) -> bool:
        """Check if the connection to the PLC simulator is alive"""
        try:
            if self.simulation_instance is not None:
                return True
            else:
                print("No simulation instance connected.")
                return False
        except Exception as e:
            print("Connection error:", e)
            return False
        
    def Disconnect(self, instance):
        """Disconnect from the PLC simulator instance"""
        try:
            if self.simulation_instance is not None:
                self.simulation_instance = None
                for inst in instance:
                    self.simulation_instance = self.manager.DestroyInterface(inst.ID)
                print("Disconnected from PLC simulator instance.")
        except Exception as e:
            print("Disconnection error:", e)

    def SetDI(self, startByte:int, bit:int, value: int):
        """
        Set a digital input (DI) bit in the PLC input process image (E/I area).

        byte: selects which input byte in the PLC is used, as defined by the GUI  
        bit: bit position (0–7) within the selected byte  
        value: True/False or 1/0 to set or clear the bit
        """
        if self.isConnected():
            if startByte >= 0 and 0 <= bit < 8:
                self.simulation_instance.InputArea.WriteBit(startByte,bit, bool(value))
    
    def GetDO(self,startbyte: int, bit: int):
        """
        Read a digital output (DO) bit from the PLC output process image (A/Q area).

        byte: selects which output byte in the PLC is used, as defined by the GUI  
        bit: bit position (0–7) within the selected byte
        """
        if self.isConnected():
            if startbyte >= 0:
                if 7 >= bit >= 0:
                    data = bytes(1)
                    data = self.simulation_instance.OutputArea.ReadBit(startbyte,bit)
                    return int(data)
            return -1


    def SetAI(self,byte: int, value: int):
        """
        Set an analog input (AI) value as a 16-bit UNSIGNED INTEGER (0–65535) in the PLC input process image (E/I area).

        byte: selects which input byte in the PLC is used, as defined by the GUI  
        value: 0–65535 (word)
        """
        if self.isConnected():
            buffer_AI = bytearray(2)
            if byte >= 0:
                if 0 <= value <= 65535:
                    lowByte = value & 0xFF  # 0xFF = mask for one byte (0b11111111)
                    highByte = (value >> 8) & 0xFF
                    buffer_AI[0] = highByte
                    buffer_AI[1] = lowByte
                    self.simulation_instance.InputArea.WriteBytes(byte,2,buffer_AI)
                    return int(value)
                return -1
            return -1


    def GetAO(self, startByte: int):
        """
        Read an analog output (AO) value as a 16-bit SIGNED INTEGER (-32768–32767) from the PLC output process image (A/Q area).

        byte: selects which output byte in the PLC is used, as defined by the GUI
        """
        if self.isConnected():
            if startByte >= 0:
                data = bytes(2)
                data = self.simulation_instance.OutputArea.ReadBytes(startByte,2)
                value = int.from_bytes(data, byteorder='big', signed = True)
                return int(value)
            
    def resetSendInputs(self, startByte: int, endByte: int):
        """
        Resets all send input data to the PLC (DI, AI)
        """
        if self.isConnected():
            if startByte >= 0 and endByte > startByte:
                size = endByte - startByte + 1
                Empty_buffer = bytearray(size)
                self.simulation_instance.InputArea.WriteBytes(startByte, size, Empty_buffer)
