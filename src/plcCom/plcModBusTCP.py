from pymodbus.client import ModbusTcpClient


class plcModBusTCP:
    """
    Klasse voor Modbus TCP communicatie met een PLC.
    """

    def __init__(self, ip: str, port: int = 502):
        self.ip = ip
        self.port = port
        self.client = None

    def connect(self):
        """Verbind met de Modbus server"""
        self.client = ModbusTcpClient(self.ip, port=self.port)
        if self.client.connect():
            print(f"Connected to Modbus server {self.ip}:{self.port}")
            self.reset_registers()
            return True
        else:
            print(f"Cannot connect to Modbus server {self.ip}:{self.port}")
            return False

    def disconnect(self):
        """Verbinding afsluiten"""
        if self.client:
            self.client.close()

    def check(self):
        """Herstel connectie indien verbroken"""
        if self.client is None or not self.client.is_socket_open():
            try:
                self.client.connect()
            except Exception as e:
                print("Can't reconnect to PLC:", e)

    def SetDI(self, index, value):
        """Schrijf een digitale input (0/1) in de databank"""
        self.check()
        if 0 <= index < 16:
            self.client.write_register(index, int(bool(value)))
            return int(bool(value))   # geef int terug
        return 0

    def SetAI(self, index, value):
        """Schrijf een analoge input (0-65535) in de databank"""
        self.check()
        if 16 <= index < 32:
            val = int(value) & 0xFFFF
            self.client.write_register(index, val)
            return val
        return 0

    def GetDO(self, index):
        """Lees een digitale output (coil)"""
        self.check()
        rr = self.client.read_coils(index, count=1)
        if rr.isError():
            return 0
        return int(rr.bits[0])   # 0 of 1

    def GetAO(self, index):
        """Lees een analoge output (holding register)"""
        self.check()
        rr = self.client.read_holding_registers(index + 32, count=1)
        if rr.isError():
            return None
        return rr.registers[0]

    def reset_registers(self):
        """Reset alle DI en AI registers naar 0"""
        for i in range(16):
            self.client.write_register(i, 0)       # DI
            self.client.write_register(i + 16, 0)  # AI
