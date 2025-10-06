import snap7
import snap7.util as s7util


class plcS7:
    """
    Klasse voor communicatie met een Siemens S7 PLC via Snap7.
    DB10 structuur:
      - 0–15   : Digitale Inputs (DI)
      - 16–31  : Digitale Outputs (DO)
      - 0–15   : Analoge Inputs (AI)
      - 0–15   : Analoge Outputs (AO)
    """

    def __init__(self, ip: str, rack: int = 0, slot: int = 1, tcpport: int = 102):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.tcpport = tcpport
        self.client = snap7.client.Client()

    def connect(self):
        """Verbind met de PLC"""
        try:
            self.client.connect(self.ip, self.rack, self.slot, self.tcpport)
            if self.client.get_connected():
                print(
                    f"Connected to S7 PLC at {self.ip}:{self.tcpport} (rack {self.rack}, slot {self.slot})")
                self.reset_registers()
                return True
            else:
                print(f"Cannot connect to S7 PLC at {self.ip}")
                return False
        except Exception as e:
            print("Connection error:", e)
            return False

    def disconnect(self):
        if self.client.get_connected():
            self.client.disconnect()

    def check(self):
        if not self.client.get_connected():
            try:
                self.client.connect(self.ip, self.rack,
                                    self.slot, self.tcpport)
            except Exception as e:
                print("Can't reconnect to PLC:", e)

    # =====================
    # Schrijven
    # =====================

    def SetDI(self, index, value, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = index // 8
            bit_index = index % 8
            data = self.client.db_read(db_number, byte_index, 1)
            s7util.set_bool(data, 0, bit_index, bool(value))
            self.client.db_write(db_number, byte_index, data)
            return int(bool(value))
        return 0

    def SetDO(self, index, value, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = 2 + index // 8
            bit_index = index % 8
            data = self.client.db_read(db_number, byte_index, 1)
            s7util.set_bool(data, 0, bit_index, bool(value))
            self.client.db_write(db_number, byte_index, data)
            return int(bool(value))
        return 0

    def SetAI(self, index, value, db_number=10):
        if 0 <= index < 16:
            self.check()
            val = int(value) & 0xFFFF
            byte_index = 4 + index * 2
            data = bytearray(2)
            s7util.set_int(data, 0, val)
            self.client.db_write(db_number, byte_index, data)
            return val
        return 0

    def SetAO(self, index, value, db_number=10):
        if 0 <= index < 16:
            self.check()
            val = int(value) & 0xFFFF
            byte_index = 36 + index * 2
            data = bytearray(2)
            s7util.set_int(data, 0, val)
            self.client.db_write(db_number, byte_index, data)
            return val
        return 0

    # =====================
    # Lezen
    # =====================

    def GetDI(self, index, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = index // 8
            bit_index = index % 8
            data = self.client.db_read(db_number, byte_index, 1)
            return int(s7util.get_bool(data, 0, bit_index))
        return 0

    def GetDO(self, index, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = 2 + index // 8
            bit_index = index % 8
            data = self.client.db_read(db_number, byte_index, 1)
            return int(s7util.get_bool(data, 0, bit_index))
        return 0

    def GetAI(self, index, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = 4 + index * 2
            data = self.client.db_read(db_number, byte_index, 2)
            return s7util.get_int(data, 0)
        return 0

    def GetAO(self, index, db_number=10):
        if 0 <= index < 16:
            self.check()
            byte_index = 36 + index * 2
            data = self.client.db_read(db_number, byte_index, 2)
            return s7util.get_int(data, 0)
        return 0

    # =====================
    # Reset
    # =====================

    def reset_registers(self, db_number=10):
        """Reset alle DI/DO/AI/AO naar 0"""
        data = bytearray(68)  # DB10 is 68 bytes groot
        self.client.db_write(db_number, 0, data)
