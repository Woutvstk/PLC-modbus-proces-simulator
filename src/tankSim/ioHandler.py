
from configuration import configuration as mainConfigClass

from tankSim.configurationTS import configuration as configurationClass
from tankSim.status import status as statusClass
from plcCom.logoS7 import logoS7
from typing import Optional, Dict, Any

class ioHandler:

    def mapValue(self, oldMin: int, oldMax: int, newMin: int, newMax: int, old: float) -> float:
        return round((old-oldMin)*(newMax-newMin)/(oldMax-oldMin)+newMin, 2)

    # plc now defined as dataType logoS7 for text color, autocomplete, ...
    # could be done cleaner/safer if all possible plcCom types are derived from a baseclass
    #ADDED optional callbacks for forcing values and status updates(IOCONFIG)
    def updateIO(self, plc: logoS7, mainConfig: mainConfigClass, config: configurationClass, status:statusClass, 
             force_callback=None, status_callback=None):
        """
        Update IO with optional force and status callbacks.
        
        Args:
            plc: PLC communication object
            config: Configuration object
            status: Status object
            force_callback: Optional callback(signal_name, io_type) -> forced_value or None
            status_callback: Optional callback(signal_name, value, io_type) to update status display
        """
        if (mainConfig.plcGuiControl == "plc"):
            # === READ PLC OUTPUTS (Simulator Inputs) ===
            
            # Check for forced values for ValveIn
            valve_in_forced = force_callback("ValveIn", "DQ") if force_callback else None
            if valve_in_forced is not None:
                status.valveInOpenFraction = float(1 if valve_in_forced else 0)
            else:
                # if DQ valveIn = 1, ignore analog setpoint
                if plc.GetDO(config.DQValveIn["byte"], config.DQValveIn["bit"]):
                    status.valveInOpenFraction = float(1)
                else:
                    status.valveInOpenFraction = self.mapValue(
                        0, plc.analogMax, 0, 1, plc.GetAO(config.AQValveInFraction["byte"]))
            
            # Update status display
            if status_callback:
                dq_value = plc.GetDO(config.DQValveIn["byte"], config.DQValveIn["bit"])
                aq_value = plc.GetAO(config.AQValveInFraction["byte"])
                status_callback("ValveIn", dq_value, "DQ")
                status_callback("ValveInFraction", aq_value, "AQ")
            
            # Check for forced values for ValveOut
            valve_out_forced = force_callback("ValveOut", "DQ") if force_callback else None
            if valve_out_forced is not None:
                status.valveOutOpenFraction = float(1 if valve_out_forced else 0)
            else:
                # if DQ valveOut = 1, ignore analog setpoint
                if plc.GetDO(config.DQValveOut["byte"], config.DQValveOut["bit"]):
                    status.valveOutOpenFraction = 1
                else:
                    status.valveOutOpenFraction = self.mapValue(
                        0, plc.analogMax, 0, 1, plc.GetAO(config.AQValveOutFraction["byte"]))
            
            # Update status display
            if status_callback:
                dq_value = plc.GetDO(config.DQValveOut["byte"], config.DQValveOut["bit"])
                aq_value = plc.GetAO(config.AQValveOutFraction["byte"])
                status_callback("ValveOut", dq_value, "DQ")
                status_callback("ValveOutFraction", aq_value, "AQ")
            
            # Check for forced values for Heater
            heater_forced = force_callback("Heater", "DQ") if force_callback else None
            if heater_forced is not None:
                status.heaterPowerFraction = float(1 if heater_forced else 0)
            else:
                # if DQ heater = 1, ignore analog setpoint
                if plc.GetDO(config.DQHeater["byte"], config.DQHeater["bit"]):
                    status.heaterPowerFraction = 1
                else:
                    status.heaterPowerFraction = plc.GetAO(
                        config.AQHeaterFraction["byte"])
            
            # Update status display
            if status_callback:
                dq_value = plc.GetDO(config.DQHeater["byte"], config.DQHeater["bit"])
                aq_value = plc.GetAO(config.AQHeaterFraction["byte"])
                status_callback("Heater", dq_value, "DQ")
                status_callback("HeaterFraction", aq_value, "AQ")
            
            # === WRITE TO PLC INPUTS (Simulator Outputs) ===
            # Check for forced sensor values
            level_high_forced = force_callback("LevelSensorHigh", "DI") if force_callback else None
            level_low_forced = force_callback("LevelSensorLow", "DI") if force_callback else None
            level_analog_forced = force_callback("LevelSensor", "AI") if force_callback else None
            temp_forced = force_callback("TemperatureSensor", "AI") if force_callback else None
            
            # Set digital level sensors (with force override)
            high_value = level_high_forced if level_high_forced is not None else status.digitalLevelSensorHighTriggered
            low_value = level_low_forced if level_low_forced is not None else status.digitalLevelSensorLowTriggered
            
            plc.SetDI(config.DILevelSensorHigh["byte"],
                    config.DILevelSensorHigh["bit"], high_value)
            plc.SetDI(config.DILevelSensorLow["byte"],
                    config.DILevelSensorLow["bit"], low_value)
            
            # Update status display
            if status_callback:
                status_callback("LevelSensorHigh", high_value, "DI")
                status_callback("LevelSensorLow", low_value, "DI")
            
            # Set analog level sensor (with force override)
            if level_analog_forced is not None:
                level_value = level_analog_forced
            else:
                level_value = self.mapValue(0, config.tankVolume, 0, plc.analogMax, status.liquidVolume)
            
            plc.SetAI(config.AILevelSensor["byte"], level_value)
            
            if status_callback:
                status_callback("LevelSensor", level_value, "AI")
            
            # Set analog temperature sensor (with force override)
            if temp_forced is not None:
                temp_value = temp_forced
            else:
                temp_value = self.mapValue(-50, 250, 0, plc.analogMax, status.liquidTemperature)
            
            plc.SetAI(config.AITemperatureSensor["byte"], temp_value)
            
            if status_callback:
                status_callback("TemperatureSensor", temp_value, "AI")

    def resetOutputs(self, mainConfig: mainConfigClass,  config: configurationClass, status: statusClass):
        # only update status if controller by plc
        if (mainConfig.plcGuiControl == "plc"):
            status.valveInOpenFraction = float(0)
            status.valveOutOpenFraction = float(0)
            status.heaterPowerFraction = float(0)
