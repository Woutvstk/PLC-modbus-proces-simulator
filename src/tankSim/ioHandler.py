
from configuration import configuration as mainConfigClass

from tankSim.configuration import configuration as configurationClass
from tankSim.status import status as statusClass
from plcCom.logoS7 import logoS7


class ioHandler:

    def mapValue(self, oldMin: int, oldMax: int, newMin: int, newMax: int, old: float) -> float:
        return round((old-oldMin)*(newMax-newMin)/(oldMax-oldMin)+newMin, 2)

    # plc now defined as dataType logoS7 for text color, autocomplete, ...
    # could be done cleaner/safer if all possible plcCom types are derived from a baseclass
    def updateIO(self, plc: logoS7, config: configurationClass, status: statusClass):
        if (config.plcGuiControl == "plc"):
            # if DQ valveIn = 1, ignore analog setpoint
            if (plc.GetDO(config.DQValveIn["byte"], config.DQValveIn["bit"])):
                status.valveInOpenFraction = float(1)
            else:
                status.valveInOpenFraction = self.mapValue(
                    0, plc.analogMax, 0, 1, plc.GetAO(config.AQValveInFraction["byte"]))

            # if DQ valveOut = 1, ignore analog setpoint
            if (plc.GetDO(config.DQValveOut["byte"], config.DQValveOut["bit"])):
                status.valveOutOpenFraction = 1
            else:
                status.valveOutOpenFraction = self.mapValue(
                    0, plc.analogMax, 0, 1, plc.GetAO(config.AQValveOutFraction["byte"]))

            # if DQ heater = 1, ignore analog setpoint
            if (plc.GetDO(config.DQHeater["byte"], config.DQHeater["bit"])):
                status.heaterPowerFraction = 1
            else:
                status.heaterPowerFraction = plc.GetAO(
                    config.AQHeaterFraction["byte"])

            # always set PLC inputs even if gui controls process
            plc.SetDI(config.DILevelSensorHigh["byte"],
                      config.DILevelSensorHigh["bit"], status.digitalLevelSensorHighTriggered)
            plc.SetDI(config.DILevelSensorLow["byte"],
                      config.DILevelSensorLow["bit"], status.digitalLevelSensorLowTriggered)
            plc.SetAI(config.AILevelSensor["byte"],
                      self.mapValue(0, config.tankVolume, 0, plc.analogMax, status.liquidVolume))
            plc.SetAI(config.AITemperatureSensor["byte"],
                      self.mapValue(-50, 250, 0, plc.analogMax, status.liquidTemperature))

    def resetOutputs(self, mainConfig: mainConfigClass,  config: configurationClass, status: statusClass):
        # only update status if controller by plc
        if (mainConfig.plcGuiControl == "plc"):
            status.valveInOpenFraction = float(0)
            status.valveOutOpenFraction = float(0)
            status.heaterPowerFraction = float(0)
