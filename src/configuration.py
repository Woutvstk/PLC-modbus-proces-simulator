

class configurationClass:

    """
    Contructor: create configuration object with default parameters
    """

    def __init__(self):

        # control process trough gui or plc
        # written by: gui
        self.plcGuiControl = "gui"  # options: gui/plc
        self.doExit = False
        """
        Plc connection settings
        """
        # written by: gui
        self.plcProtocol: str = "logoS7"
        self.plcIpAdress: str = "192.168.0.1"
        self.plcPort: int = 502
        self.plcRack: int = 0
        self.plcSlot: int = 1
        self.tsapLogo: int = 0x0300
        self.tsapServer: int = 0x2000
        # set True by gui, set False by main
        self.tryConnect: bool = False
        """
        IO settings
        """

        # PLC OUTPUTS
        # DIGITAL
        self.DQValveIn = {"byte": 0, "bit": 0}   # False = Closed
        self.DQValveOut = {"byte": 0, "bit": 1}  # False = Closed
        self.DQHeater = {"byte": 0, "bit": 2}    # False = Off
        # ANALOG
        self.AQValveInFraction = {"byte": 2}     # 0 = Closed, MAX = full open
        self.AQValveOutFraction = {"byte": 4}    # 0 = Closed, MAX = full open
        self.AQHeaterFraction = {"byte": 6}      # 0 = Off, MAX = full power

        # PLC INPUTS
        # DIGITAL
        self.DILevelSensorHigh = {"byte": 0, "bit": 0}  # False = liquid below sensor
        self.DILevelSensorLow = {"byte": 0, "bit": 1}   # False = liquid below sensor
        # ANALOG
        self.AILevelSensor = {"byte": 2}                # 0 = empty tank, MAX = full tank
        self.AITemperatureSensor = {"byte": 4}          # 0 = -50°C, MAX = 250°C

        self.lowestByte, self.highestByte = self.get_byte_range()

        """
        Simulation settings
        """
        self.simulationInterval = 0.2  # in seconds
        """
        process settings
        """
        self.tankVolume = 200
        self.valveInMaxFlow = 5
        self.valveOutMaxFlow = 2
        self.ambientTemp = 21
        # default at 90%
        self.digitalLevelSensorHighTriggerLevel = 0.9 * self.tankVolume
        # default at 10%
        self.digitalLevelSensorLowTriggerLevel = 0.1 * self.tankVolume
        # heater power in watts
        self.heaterMaxPower = 10000
        # tank heat loss
        self.tankHeatLoss = 150
        # specific heat capacity in Joeles/Kg*°C (4186 for water)
        self.liquidSpecificHeatCapacity: float = 4186
        # specific weight in kg per liter (water: 1)
        self.liquidSpecificWeight: float = 1
        # initialize liquid temp at ambient
        self.liquidTemperature = self.ambientTemp
        # boiling temperature of liquid (water: 100)
        self.liquidBoilingTemp = 100


    def get_byte_range(self):
        """
        Return the lowest and highest byte used in all IO definitions.
        Scans all dicts in the current object that have a 'byte' key.
        """
        #function used for resetSendInputs in plcCom
        bytes_used = []

        for _, value in self.__dict__.items():
            # Controleer of de waarde een dictionary is met een 'byte'-sleutel
            if isinstance(value, dict) and "byte" in value:
                # Voeg de byte-waarde toe aan de lijst met gebruikte bytes
                bytes_used.append(value["byte"])

        # Als er minstens één byte gevonden is → bepaal laagste en hoogste
        if bytes_used:
            lowest = min(bytes_used)
            highest = max(bytes_used)
            return lowest, highest
        else:
            return None, None

    # ----------------------------------------------------------
    def update_io_range(self):
        """
        Call this when IO data changes (e.g. GUI edits addresses).
        """
        self.lowestByte, self.highestByte = self.get_byte_range()
