
class statusClass:
    def __init__(self):
        # valve IN status
        # written by: plc or gui
        self.valveInOpenFraction: float = 0

        # valve OUT status
        # written by: plc or gui
        self.valveOutOpenFraction: float = 0

        # heating element status
        # written by: plc or gui
        self.heaterPowerFraction: float = 0

        # digital level sensor status
        # written by: procesSim
        self.digitalLevelSensorLowTriggered: bool = False
        self.digitalLevelSensorHighTriggered: bool = False

        # liquid parameters
        # written by: procesSim
        self.liquidVolume = 100
        # initialize liquid temp
        # written by: procesSim
        self.liquidTemperature = 0

        # simulation status
        # written by: gui
        self.simRunning = False

        # flow rates
        # written by process
        self.flowRateIn = 0
        self.flowRateOut = 0
