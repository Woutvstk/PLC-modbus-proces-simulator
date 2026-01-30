"""
Save/Load Page Mixin - Handles save/load button functionality.

This mixin provides:
- Save button handlers (pushButton_Save2, pushButton_Save)
- Load button handlers (pushButton_Load2, pushButton_Load)
- File dialog integration
- State validation and error handling
- GUI updates after load

External Libraries Used:
- PyQt5 (GPL v3) - GUI framework and file dialogs
- logging (Python Standard Library) - Error and info logging
- pathlib (Python Standard Library) - File path handling
"""
import logging
import time
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QPushButton, QSlider, QLineEdit, QRadioButton
from PyQt5.QtCore import QTimer

from core.load_save import save_application_state, load_application_state, validate_state_file

logger = logging.getLogger(__name__)


class SaveLoadMixin:
    """
    Mixin class for save/load functionality.
    Combined with MainWindow via multiple inheritance.
    """

    def init_save_load_page(self):
        """Initialize save/load button connections."""
        try:
            # Connect Save buttons
            if hasattr(self, 'pushButton_Save'):
                self.pushButton_Save.clicked.connect(self.on_save_clicked)
            
            if hasattr(self, 'pushButton_Save2'):
                self.pushButton_Save2.clicked.connect(self.on_save_clicked)
            
            # Connect Load buttons
            if hasattr(self, 'pushButton_Load'):
                self.pushButton_Load.clicked.connect(self.on_load_clicked)
            
            if hasattr(self, 'pushButton_Load2'):
                self.pushButton_Load2.clicked.connect(self.on_load_clicked)
            
            logger.info("Save/Load buttons initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize save/load buttons: {e}")

    def on_save_clicked(self):
        """Handle save button click - prompts for file and saves complete state."""
        try:
            # Get file path from user
            default_path = Path.cwd() / "saved_states"
            default_path.mkdir(exist_ok=True)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Application State",
                str(default_path / "simulation_state.json"),
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if not file_path:
                # User cancelled
                return
            
            # Ensure .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            # Get paths
            src_dir = Path(__file__).resolve().parent.parent.parent
            io_config_path = src_dir / "IO" / "IO_configuration.json"
            
            # Get simulation manager from mainConfig
            simulation_manager = None
            if hasattr(self, 'mainConfig') and hasattr(self.mainConfig, 'simulationManager'):
                simulation_manager = self.mainConfig.simulationManager
            
            # Sync GUI states to status/config before saving
            try:
                if simulation_manager:
                    active_sim = simulation_manager.get_active_simulation()
                    
                    # DON'T sync simRunning - we don't want to auto-start the simulation on load
                    # User explicitly requested simRunning should NOT be saved
                    
                    if active_sim and hasattr(active_sim, 'status'):
                        try:
                            # Sync PID valve control states to status
                            
                            # Auto/Manual mode buttons
                            auto_btn = self.findChild(QPushButton, "pushButton_PidValveAuto")
                            man_btn = self.findChild(QPushButton, "pushButton_PidValveMan")
                            if auto_btn and man_btn:
                                active_sim.status.pidPidValveAutoCmd = auto_btn.isChecked()
                                active_sim.status.pidPidValveManCmd = man_btn.isChecked()
                                logger.info(f"    ✓ Synced Auto/Man: Auto={auto_btn.isChecked()}, Man={man_btn.isChecked()}")
                            
                            # Temperature control radio buttons (Analog/Digital)
                            radio_ai_temp = self.findChild(QRadioButton, "radioButton_PidTankValveAItemp")
                            radio_di_temp = self.findChild(QRadioButton, "radioButton_PidTankValveDItemp")
                            if radio_ai_temp and radio_di_temp:
                                active_sim.status.pidPidTankValveAItempCmd = radio_ai_temp.isChecked()
                                active_sim.status.pidPidTankValveDItempCmd = radio_di_temp.isChecked()
                                logger.info(f"    ✓ Synced Temp control: AI={radio_ai_temp.isChecked()}, DI={radio_di_temp.isChecked()}")
                            
                            # Level control radio buttons (Analog/Digital)
                            radio_ai_level = self.findChild(QRadioButton, "radioButton_PidTankValveAIlevel")
                            radio_di_level = self.findChild(QRadioButton, "radioButton_PidTankValveDIlevel")
                            if radio_ai_level and radio_di_level:
                                active_sim.status.pidPidTankValveAIlevelCmd = radio_ai_level.isChecked()
                                active_sim.status.pidPidTankValveDIlevelCmd = radio_di_level.isChecked()
                                logger.info(f"    ✓ Synced Level control: AI={radio_ai_level.isChecked()}, DI={radio_di_level.isChecked()}")
                            
                            # Heater power slider (0-100%)
                            heater_sliders = [
                                self.findChild(QSlider, "heaterPowerSlider"),
                                self.findChild(QSlider, "heaterPowerSlider_1"),
                                self.findChild(QSlider, "heaterPowerSlider_2"),
                                self.findChild(QSlider, "heaterPowerSlider_3")
                            ]
                            for slider in heater_sliders:
                                if slider:
                                    # Slider is 0-100, status is 0.0-1.0
                                    active_sim.status.heaterPowerFraction = slider.value() / 100.0
                                    logger.info(f"    ✓ Synced heater power: {slider.value()}% ({active_sim.status.heaterPowerFraction:.2f})")
                                    break
                            
                            # Temperature setpoint slider (0-27648 range)
                            slider_temp = self.findChild(QSlider, "slider_PidTankTempSP")
                            if slider_temp:
                                active_sim.status.pidPidTankTempSPValue = slider_temp.value()
                                logger.info(f"    ✓ Synced temp setpoint: {slider_temp.value()}")
                            
                            # Level setpoint slider (0-27648 range)
                            slider_level = self.findChild(QSlider, "slider_PidTankLevelSP")
                            if slider_level:
                                active_sim.status.pidPidTankLevelSPValue = slider_level.value()
                                logger.info(f"    ✓ Synced level setpoint: {slider_level.value()}")
                            
                            # Valve positions from entry fields (manual mode) - convert to fractions
                            valve_in_entry = self.findChild(QLineEdit, "valveInEntry")
                            if valve_in_entry:
                                try:
                                    val = float(valve_in_entry.text() or 0)
                                    active_sim.status.valveInOpenFraction = val / 100.0  # Convert % to fraction
                                    logger.info(f"    ✓ Synced valve in: {val}% ({active_sim.status.valveInOpenFraction:.2f})")
                                except ValueError:
                                    pass
                            
                            valve_out_entry = self.findChild(QLineEdit, "valveOutEntry")
                            if valve_out_entry:
                                try:
                                    val = float(valve_out_entry.text() or 0)
                                    active_sim.status.valveOutOpenFraction = val / 100.0  # Convert % to fraction
                                    logger.info(f"    ✓ Synced valve out: {val}% ({active_sim.status.valveOutOpenFraction:.2f})")
                                except ValueError:
                                    pass
                            
                        except Exception as e:
                            logger.warning(f"    Could not sync PID control states: {e}", exc_info=True)
                    
                    # Sync GUI display settings and configuration parameters to config before saving
                    if active_sim and hasattr(active_sim, 'config'):
                        try:
                            # Tank volume (convert m³ to liters)
                            volumeEntry = self.findChild(QLineEdit, "volumeEntry")
                            if volumeEntry and volumeEntry.text():
                                try:
                                    volume_m3 = float(volumeEntry.text())
                                    active_sim.config.tankVolume = volume_m3 * 1000.0  # Convert m³ to L
                                    logger.info(f"    ✓ Synced tankVolume: {volume_m3} m³ ({active_sim.config.tankVolume} L)")
                                except ValueError:
                                    pass
                            
                            # Flow rates
                            maxFlowInEntry = self.findChild(QLineEdit, "maxFlowInEntry")
                            if maxFlowInEntry and maxFlowInEntry.text():
                                try:
                                    active_sim.config.valveInMaxFlow = float(maxFlowInEntry.text())
                                    logger.info(f"    ✓ Synced valveInMaxFlow: {active_sim.config.valveInMaxFlow}")
                                except ValueError:
                                    pass
                            
                            maxFlowOutEntry = self.findChild(QLineEdit, "maxFlowOutEntry")
                            if maxFlowOutEntry and maxFlowOutEntry.text():
                                try:
                                    active_sim.config.valveOutMaxFlow = float(maxFlowOutEntry.text())
                                    logger.info(f"    ✓ Synced valveOutMaxFlow: {active_sim.config.valveOutMaxFlow}")
                                except ValueError:
                                    pass
                            
                            # Ambient temperature
                            ambientTempEntry = self.findChild(QLineEdit, "ambientTempEntry")
                            if ambientTempEntry and ambientTempEntry.text():
                                try:
                                    active_sim.config.ambientTemp = float(ambientTempEntry.text())
                                    logger.info(f"    ✓ Synced ambientTemp: {active_sim.config.ambientTemp}")
                                except ValueError:
                                    pass
                            
                            # Heater power (convert kW to W)
                            powerHeatingCoilEntry = self.findChild(QLineEdit, "powerHeatingCoilEntry")
                            if powerHeatingCoilEntry and powerHeatingCoilEntry.text():
                                try:
                                    power_kw = float(powerHeatingCoilEntry.text())
                                    active_sim.config.heaterMaxPower = power_kw * 1000.0  # Convert kW to W
                                    logger.info(f"    ✓ Synced heaterMaxPower: {power_kw} kW ({active_sim.config.heaterMaxPower} W)")
                                except ValueError:
                                    pass
                            
                            # Heat loss
                            heatLossVatEntry = self.findChild(QLineEdit, "heatLossVatEntry")
                            if heatLossVatEntry and heatLossVatEntry.text():
                                try:
                                    active_sim.config.tankHeatLoss = float(heatLossVatEntry.text())
                                    logger.info(f"    ✓ Synced tankHeatLoss: {active_sim.config.tankHeatLoss}")
                                except ValueError:
                                    pass
                            
                            # Level sensor thresholds
                            levelSwitchMaxHeightEntry = self.findChild(QLineEdit, "levelSwitchMaxHeightEntry")
                            if levelSwitchMaxHeightEntry and levelSwitchMaxHeightEntry.text():
                                try:
                                    active_sim.config.digitalLevelSensorHighTriggerLevel = float(levelSwitchMaxHeightEntry.text())
                                    logger.info(f"    ✓ Synced digitalLevelSensorHighTriggerLevel: {active_sim.config.digitalLevelSensorHighTriggerLevel}")
                                except ValueError:
                                    pass
                            
                            levelSwitchMinHeightEntry = self.findChild(QLineEdit, "levelSwitchMinHeightEntry")
                            if levelSwitchMinHeightEntry and levelSwitchMinHeightEntry.text():
                                try:
                                    active_sim.config.digitalLevelSensorLowTriggerLevel = float(levelSwitchMinHeightEntry.text())
                                    logger.info(f"    ✓ Synced digitalLevelSensorLowTriggerLevel: {active_sim.config.digitalLevelSensorLowTriggerLevel}")
                                except ValueError:
                                    pass
                            
                            # Liquid properties
                            specificHeatCapacityEntry = self.findChild(QLineEdit, "specificHeatCapacityEntry")
                            if specificHeatCapacityEntry and specificHeatCapacityEntry.text():
                                try:
                                    active_sim.config.liquidSpecificHeatCapacity = float(specificHeatCapacityEntry.text())
                                    logger.info(f"    ✓ Synced liquidSpecificHeatCapacity: {active_sim.config.liquidSpecificHeatCapacity}")
                                except ValueError:
                                    pass
                            
                            specificWeightEntry = self.findChild(QLineEdit, "specificWeightEntry")
                            if specificWeightEntry and specificWeightEntry.text():
                                try:
                                    active_sim.config.liquidSpecificWeight = float(specificWeightEntry.text())
                                    logger.info(f"    ✓ Synced liquidSpecificWeight: {active_sim.config.liquidSpecificWeight}")
                                except ValueError:
                                    pass
                            
                            boilingTempEntry = self.findChild(QLineEdit, "boilingTempEntry")
                            if boilingTempEntry and boilingTempEntry.text():
                                try:
                                    active_sim.config.liquidBoilingTemp = float(boilingTempEntry.text())
                                    logger.info(f"    ✓ Synced liquidBoilingTemp: {active_sim.config.liquidBoilingTemp}")
                                except ValueError:
                                    pass
                            
                            # Time delays
                            timeDelayfillingEntry = self.findChild(QLineEdit, "timeDelayfillingEntry")
                            if timeDelayfillingEntry and timeDelayfillingEntry.text():
                                try:
                                    active_sim.config.liquidVolumeTimeDelay = float(timeDelayfillingEntry.text())
                                    logger.info(f"    ✓ Synced liquidVolumeTimeDelay: {active_sim.config.liquidVolumeTimeDelay}")
                                except ValueError:
                                    pass
                            
                            timeDelayTempEntry = self.findChild(QLineEdit, "timeDelayTempEntry")
                            if timeDelayTempEntry and timeDelayTempEntry.text():
                                try:
                                    active_sim.config.liquidTempTimeDelay = float(timeDelayTempEntry.text())
                                    logger.info(f"    ✓ Synced liquidTempTimeDelay: {active_sim.config.liquidTempTimeDelay}")
                                except ValueError:
                                    pass
                            
                            # Tank color from dropdown
                            if hasattr(self, 'colorDropDown') and self.colorDropDown:
                                tank_color = self.colorDropDown.currentData()
                                if tank_color:
                                    active_sim.config.tankColor = tank_color
                                    logger.info(f"    ✓ Synced tankColor: {tank_color}")
                            
<<<<<<< Updated upstream
                            # Display checkboxes
                            if hasattr(self, 'levelSwitchesCheckBox') and self.levelSwitchesCheckBox:
                                active_sim.config.displayLevelSwitches = self.levelSwitchesCheckBox.isChecked()
                                logger.info(f"    ✓ Synced displayLevelSwitches: {self.levelSwitchesCheckBox.isChecked()}")
=======
                            # Display checkboxes - CRITICAL FIX
                            levelSwitchesCheckBox = self.findChild(QWidget, "levelSwitchesCheckBox")
                            if levelSwitchesCheckBox:
                                active_sim.config.displayLevelSwitches = levelSwitchesCheckBox.isChecked()
                                logger.info(f"    ✓ Synced displayLevelSwitches: {levelSwitchesCheckBox.isChecked()}")
>>>>>>> Stashed changes
                            
                            if hasattr(self, 'analogValueTempCheckBox') and self.analogValueTempCheckBox:
                                active_sim.config.displayTemperature = self.analogValueTempCheckBox.isChecked()
                                logger.info(f"    ✓ Synced displayTemperature: {self.analogValueTempCheckBox.isChecked()}")
                        except Exception as e:
                            logger.warning(f"    Could not sync configuration to config object: {e}", exc_info=True)
            except Exception as e:
                logger.warning(f"Could not sync status/config before save: {e}", exc_info=True)
            
            # Save state
            logger.info(f"Saving state to: {file_path}")
            
            success = save_application_state(
                main_config=self.mainConfig,
                simulation_manager=simulation_manager,
                io_config_path=str(io_config_path),
                save_file_path=file_path
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"Application state saved successfully to:\n{file_path}\n\n"
                    f"This file contains:\n"
                    f"• Main configuration (PLC settings, protocol)\n"
                    f"• Simulation configuration\n"
                    f"• Current process values\n"
                    f"• IO configuration"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save application state to:\n{file_path}\n\n"
                    f"Check the log for details."
                )
                
        except Exception as e:
            logger.error(f"Error during save: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving:\n{str(e)}"
            )

    def on_load_clicked(self):
        """Handle load button click - prompts for file and loads complete state."""
        try:
            # Get file path from user
            default_path = Path.cwd() / "saved_states"
            default_path.mkdir(exist_ok=True)
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Application State",
                str(default_path),
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if not file_path:
                # User cancelled
                return
            
            # Validate file first (single popup flow)
            is_valid, message = validate_state_file(file_path)
            
            if not is_valid:
                QMessageBox.critical(
                    self,
                    "Invalid State File",
                    f"The selected file is not a valid state file:\n\n{message}"
                )
                return
            
            # Get paths
            src_dir = Path(__file__).resolve().parent.parent.parent
            io_config_output_path = src_dir / "IO" / "IO_configuration.json"
            
            # Get simulation manager from mainConfig
            simulation_manager = None
            if hasattr(self, 'mainConfig') and hasattr(self.mainConfig, 'simulationManager'):
                simulation_manager = self.mainConfig.simulationManager
            
            # Load state
            logger.info(f"Loading state from: {file_path}")
            
            success = load_application_state(
                main_config=self.mainConfig,
                simulation_manager=simulation_manager,
                io_config_output_path=str(io_config_output_path),
                load_file_path=file_path
            )
            
            if success:
                # Reload IO configuration in the active simulation
                self._reload_io_config_after_load(str(io_config_output_path))

                # Push loaded config/status into GUI fields to avoid defaults overwriting
                try:
                    if simulation_manager:
                        sim = simulation_manager.get_active_simulation()
                        if sim and hasattr(self, 'apply_loaded_state_to_gui'):
                            logger.info(">>> Calling apply_loaded_state_to_gui...")
                            self.apply_loaded_state_to_gui(
                                getattr(sim, 'config', None),
                                getattr(sim, 'status', None)
                            )
                            logger.info(">>> ✓ State applied to GUI")
                except Exception as e:
                    logger.error(f"ERROR: Could not apply loaded state to GUI fields: {e}", exc_info=True)
                
                # Update GUI to reflect loaded state
                self._update_gui_after_load()
                
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Application state loaded successfully from:\n{file_path}\n\n"
                    f"{message}\n\n"
                    f"The application is now ready to run with the loaded configuration."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Load Failed",
                    f"Failed to load application state from:\n{file_path}\n\n"
                    f"Check the log for details."
                )
                
        except Exception as e:
            logger.error(f"Error during load: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Load Error",
                f"An error occurred while loading:\n{str(e)}"
            )

    def _reload_io_config_after_load(self, io_config_path: str):
        """
        Reload IO configuration after loading state.
        
        Args:
            io_config_path: Path to IO configuration file
        """
        try:
            logger.info(f">>> Reloading IO config from: {io_config_path}")
            # Get active simulation
            simulation_manager = None
            if hasattr(self, 'mainConfig') and hasattr(self.mainConfig, 'simulationManager'):
                simulation_manager = self.mainConfig.simulationManager
            
            if simulation_manager:
                active_sim = simulation_manager.get_active_simulation()
                if active_sim and hasattr(active_sim, 'config'):
                    # Reload IO config
                    active_sim.config.load_io_config_from_file(io_config_path)
                    logger.info(f"    ✓ IO configuration loaded from: {io_config_path}")
                    
                    # Update GUI references
                    if hasattr(self, 'tanksim_config'):
                        self.tanksim_config = active_sim.config
                    
                    if hasattr(self, 'tanksim_status'):
                        self.set_simulation_status(active_sim.status)
                    
                    # Apply loaded IO config to GUI table
                    try:
                        if hasattr(self, 'apply_loaded_io_config'):
                            logger.info("    >>> Applying loaded IO config to GUI table...")
                            result = self.apply_loaded_io_config(Path(io_config_path))
                            logger.info(f"    ✓ IO config applied to GUI: {result}")
                    except Exception as e:
                        logger.error(f"    ERROR: Could not apply loaded IO config to GUI: {e}", exc_info=True)
                    
                    # Start forced write period for IO handler
                    if hasattr(self, 'mainConfig') and hasattr(self.mainConfig, 'ioHandler'):
                        self.mainConfig.ioHandler.start_force_write_period()
                        logger.info("    ✓ Started IO forced write period after load")
                        
        except Exception as e:
            logger.error(f"ERROR: Failed to reload IO config after load: {e}", exc_info=True)

    def _update_gui_after_load(self):
        """Update GUI elements after loading state."""
        try:
            # Update controller dropdown to match loaded protocol
            if hasattr(self, 'controlerDropDown') and hasattr(self, 'mainConfig'):
                protocol = self.mainConfig.plcProtocol
                
                # Map protocol to dropdown text
                protocol_map = {
                    "GUI": "GUI (MIL)",
                    "logo!": "logo! (HIL)",
                    "PLC S7-1500/1200/400/300/ET 200SP": "PLC S7-1500/1200/400/300/ET 200SP (HIL)",
                    "PLCSim S7-1500 advanced": "PLCSim S7-1500 advanced (SIL)",
                    "PLCSim S7-1500/1200/400/300/ET 200SP": "PLCSim S7-1500/1200/400/300/ET 200SP (SIL)"
                }
                
                dropdown_text = protocol_map.get(protocol, protocol)
                
                # Block signals to prevent triggering connection attempts
                self.controlerDropDown.blockSignals(True)
                
                # Try exact display text match first
                if self.controlerDropDown.findText(dropdown_text) >= 0:
                    self.controlerDropDown.setCurrentText(dropdown_text)
                else:
                    # Fallback: try to match by base protocol name (e.g., 'logo!')
                    matched = False
                    for i in range(self.controlerDropDown.count()):
                        item = self.controlerDropDown.itemText(i)
                        if item.startswith(protocol):
                            self.controlerDropDown.setCurrentIndex(i)
                            matched = True
                            break
                    if not matched:
                        # Last resort: set text directly (may not be present in list)
                        self.controlerDropDown.setCurrentText(dropdown_text)
                
                self.controlerDropDown.blockSignals(False)
                
                # Ensure mainConfig matches what we just set (avoid races)
                try:
                    self.mainConfig.plcProtocol = protocol
                except Exception:
                    pass
                
                # Update active method label
                if hasattr(self, '_update_active_method_label'):
                    self._update_active_method_label(protocol)
            
            # Update IP address field
            if hasattr(self, 'lineEdit_IPAddress') and hasattr(self, 'mainConfig'):
                self.lineEdit_IPAddress.blockSignals(True)
                self.lineEdit_IPAddress.setText(self.mainConfig.plcIpAdress)
                self.lineEdit_IPAddress.blockSignals(False)
            
            # Update network adapter selection
            if hasattr(self, 'comboBox_networkPort') and hasattr(self, 'mainConfig'):
                adapter = self.mainConfig.selectedNetworkAdapter
                self.comboBox_networkPort.blockSignals(True)
                index = self.comboBox_networkPort.findText(adapter)
                if index >= 0:
                    self.comboBox_networkPort.setCurrentIndex(index)
                self.comboBox_networkPort.blockSignals(False)
            
            # Disconnect if currently connected (state was loaded, connection is invalid)
            if hasattr(self, 'pushButton_connect'):
                if self.pushButton_connect.isChecked():
                    self.pushButton_connect.blockSignals(True)
                    self.pushButton_connect.setChecked(False)
                    self.pushButton_connect.blockSignals(False)
                    
                    # Update connection state
                    self.validPlcConnection = False
                    self.plc = None
                    
                    # Update icon
                    if hasattr(self, 'update_connection_status_icon'):
                        self.update_connection_status_icon()
            
            # Enable/disable connect button based on protocol
            if hasattr(self, 'pushButton_connect') and hasattr(self, 'mainConfig'):
                is_gui_mode = self.mainConfig.plcProtocol == "GUI"
                self.pushButton_connect.setEnabled(not is_gui_mode)
                if hasattr(self, 'lineEdit_IPAddress'):
                    self.lineEdit_IPAddress.setEnabled(not is_gui_mode)
            
            # Prevent GUI controls from overwriting freshly loaded status for a short window
            try:
                self._suppress_gui_to_status_until = time.monotonic() + 1.0
            except Exception:
                pass
            
            # Update window references to loaded simulation
            try:
                if hasattr(self, 'mainConfig') and hasattr(self.mainConfig, 'simulationManager'):
                    simulation_manager = self.mainConfig.simulationManager
                    active_sim = simulation_manager.get_active_simulation()
                    active_sim_name = simulation_manager.get_active_simulation_name()
                    
                    if active_sim:
                        # Update window references
                        self.tanksim_config = active_sim.config
                        self.set_simulation_status(active_sim.status)
                        logger.info(f"    ✓ Updated window references to loaded simulation: {active_sim_name}")
                        
                        # Map simulation name to page index
                        sim_name_to_index = {
                            "PIDtankValve": 0,
                            "dualTank": 1,
                            "conveyor": 2
                        }
                        
                        # Open the correct simulation page (singleTankPage, dualTankPage, conveyorPage)
                        sim_index = sim_name_to_index.get(active_sim_name)
                        if sim_index is not None and hasattr(self, 'start_simulation'):
                            try:
                                self.start_simulation(sim_index)
                                logger.info(f"    ✓ Opened {active_sim_name} page (index {sim_index})")
                            except Exception as e:
                                logger.warning(f"    Failed to open simulation page: {e}", exc_info=True)
                        
                        # DON'T auto-start simulation on load - user explicitly requested this
                        # simRunning is not saved, so simulation stays stopped
                        logger.info(f"    Simulation will NOT auto-start (simRunning not saved)")
            except Exception as e:
                logger.error(f"Failed to update simulation references: {e}", exc_info=True)

            # Trigger an immediate display refresh from loaded status/config
            try:
                if hasattr(self, 'update_tanksim_display'):
                    self.update_tanksim_display()
                if hasattr(self, '_update_general_controls_ui'):
                    self._update_general_controls_ui()
            except Exception:
                pass
            
            logger.info("GUI updated after state load")
            
        except Exception as e:
            logger.error(f"Failed to update GUI after load: {e}", exc_info=True)
    
    def apply_loaded_state_to_gui(self, config, status):
        """
        Apply loaded simulation config and status to GUI fields.
        
        This function populates the GUI with values from the loaded configuration
        and status objects, ensuring the display reflects the saved state.
        
        Args:
            config: Loaded simulation configuration object
            status: Loaded simulation status object
        """
        try:
            if not config and not status:
                logger.warning("apply_loaded_state_to_gui: No config or status provided")
                return
            
            logger.info(">>> apply_loaded_state_to_gui: Starting to apply loaded config/status to GUI fields...")
            
<<<<<<< Updated upstream
            # SECTION 1: Apply configuration values to entry fields
            if config:
                try:
                    count = 0
                    
                    # Tank volume (convert liters to m³)
                    if hasattr(config, 'tankVolume') and hasattr(self, 'volumeEntry'):
                        volume_m3 = config.tankVolume / 1000.0
                        self.volumeEntry.blockSignals(True)
                        self.volumeEntry.setText(str(round(volume_m3, 2)))
                        self.volumeEntry.blockSignals(False)
                        logger.info(f"    ✓ tankVolume: {config.tankVolume} L")
                        count += 1
=======
            # Debug: Check if simSettings page is available
            if not hasattr(self, 'volumeEntry'):
                logger.warning(">>> apply_loaded_state_to_gui: volumeEntry not found - GUI may not be initialized")
                logger.info(">>> Attempting to find widgets from simSettings mixin...")
            
            # SECTION 1: Apply configuration values to entry fields
            if config:
                try:
                    # Tank parameters
                    if hasattr(config, 'tankVolume'):
                        volume_m3 = config.tankVolume / 1000.0  # Convert liters to m³
                        if hasattr(self, 'volumeEntry') and self.volumeEntry:
                            self.volumeEntry.blockSignals(True)
                            self.volumeEntry.setText(str(round(volume_m3, 2)))
                            self.volumeEntry.blockSignals(False)
                            logger.info(f"    ✓ tankVolume: {config.tankVolume} L ({volume_m3:.2f} m³)")
                        else:
                            logger.warning(f"    ⚠ volumeEntry widget not found, skipping")
>>>>>>> Stashed changes
                    
                    # Flow rates
                    if hasattr(config, 'valveInMaxFlow') and hasattr(self, 'maxFlowInEntry'):
                        self.maxFlowInEntry.blockSignals(True)
                        self.maxFlowInEntry.setText(str(config.valveInMaxFlow))
                        self.maxFlowInEntry.blockSignals(False)
<<<<<<< Updated upstream
                        logger.info(f"    ✓ valveInMaxFlow: {config.valveInMaxFlow}")
                        count += 1
=======
                        # Sync to linked fields
                        if hasattr(self, 'maxFlowInEntry1') and hasattr(self, 'maxFlowInEntry2'):
                            self.maxFlowInEntry1.blockSignals(True)
                            self.maxFlowInEntry1.setText(str(config.valveInMaxFlow))
                            self.maxFlowInEntry1.blockSignals(False)
                            self.maxFlowInEntry2.blockSignals(True)
                            self.maxFlowInEntry2.setText(str(config.valveInMaxFlow))
                            self.maxFlowInEntry2.blockSignals(False)
                        logger.info(f"    ✓ valveInMaxFlow: {config.valveInMaxFlow}")
>>>>>>> Stashed changes
                    
                    if hasattr(config, 'valveOutMaxFlow') and hasattr(self, 'maxFlowOutEntry'):
                        self.maxFlowOutEntry.blockSignals(True)
                        self.maxFlowOutEntry.setText(str(config.valveOutMaxFlow))
                        self.maxFlowOutEntry.blockSignals(False)
                        logger.info(f"    ✓ valveOutMaxFlow: {config.valveOutMaxFlow}")
<<<<<<< Updated upstream
                        count += 1
=======
>>>>>>> Stashed changes
                    
                    # Ambient temperature
                    if hasattr(config, 'ambientTemp') and hasattr(self, 'ambientTempEntry'):
                        self.ambientTempEntry.blockSignals(True)
                        self.ambientTempEntry.setText(str(config.ambientTemp))
                        self.ambientTempEntry.blockSignals(False)
                        logger.info(f"    ✓ ambientTemp: {config.ambientTemp}")
<<<<<<< Updated upstream
                        count += 1
                    
                    # Heater power (convert W to kW)
                    if hasattr(config, 'heaterMaxPower') and hasattr(self, 'powerHeatingCoilEntry'):
                        power_kw = config.heaterMaxPower / 1000.0
=======
                    
                    # Heater power
                    if hasattr(config, 'heaterMaxPower') and hasattr(self, 'powerHeatingCoilEntry'):
                        power_kw = config.heaterMaxPower / 1000.0  # Convert W to kW
>>>>>>> Stashed changes
                        self.powerHeatingCoilEntry.blockSignals(True)
                        self.powerHeatingCoilEntry.setText(str(round(power_kw, 2)))
                        self.powerHeatingCoilEntry.blockSignals(False)
                        logger.info(f"    ✓ heaterMaxPower: {config.heaterMaxPower} W")
<<<<<<< Updated upstream
                        count += 1
=======
                    
                    # Heat loss
                    if hasattr(config, 'tankHeatLoss') and hasattr(self, 'heatLossVatEntry'):
                        self.heatLossVatEntry.blockSignals(True)
                        self.heatLossVatEntry.setText(str(config.tankHeatLoss))
                        self.heatLossVatEntry.blockSignals(False)
                        logger.info(f"    ✓ tankHeatLoss: {config.tankHeatLoss}")
                    
                    # Level sensor thresholds
                    if hasattr(config, 'digitalLevelSensorHighTriggerLevel') and hasattr(self, 'levelSwitchMaxHeightEntry'):
                        self.levelSwitchMaxHeightEntry.blockSignals(True)
                        self.levelSwitchMaxHeightEntry.setText(str(config.digitalLevelSensorHighTriggerLevel))
                        self.levelSwitchMaxHeightEntry.blockSignals(False)
                        logger.info(f"    ✓ digitalLevelSensorHighTriggerLevel: {config.digitalLevelSensorHighTriggerLevel}")
                    
                    if hasattr(config, 'digitalLevelSensorLowTriggerLevel') and hasattr(self, 'levelSwitchMinHeightEntry'):
                        self.levelSwitchMinHeightEntry.blockSignals(True)
                        self.levelSwitchMinHeightEntry.setText(str(config.digitalLevelSensorLowTriggerLevel))
                        self.levelSwitchMinHeightEntry.blockSignals(False)
                        logger.info(f"    ✓ digitalLevelSensorLowTriggerLevel: {config.digitalLevelSensorLowTriggerLevel}")
                    
                    # Liquid properties
                    if hasattr(config, 'liquidSpecificHeatCapacity') and hasattr(self, 'specificHeatCapacityEntry'):
                        self.specificHeatCapacityEntry.blockSignals(True)
                        self.specificHeatCapacityEntry.setText(str(config.liquidSpecificHeatCapacity))
                        self.specificHeatCapacityEntry.blockSignals(False)
                        logger.info(f"    ✓ liquidSpecificHeatCapacity: {config.liquidSpecificHeatCapacity}")
                    
                    if hasattr(config, 'liquidSpecificWeight') and hasattr(self, 'specificWeightEntry'):
                        self.specificWeightEntry.blockSignals(True)
                        self.specificWeightEntry.setText(str(config.liquidSpecificWeight))
                        self.specificWeightEntry.blockSignals(False)
                        logger.info(f"    ✓ liquidSpecificWeight: {config.liquidSpecificWeight}")
                    
                    if hasattr(config, 'liquidBoilingTemp') and hasattr(self, 'boilingTempEntry'):
                        self.boilingTempEntry.blockSignals(True)
                        self.boilingTempEntry.setText(str(config.liquidBoilingTemp))
                        self.boilingTempEntry.blockSignals(False)
                        logger.info(f"    ✓ liquidBoilingTemp: {config.liquidBoilingTemp}")
                    
                    # Time delays
                    if hasattr(config, 'liquidVolumeTimeDelay') and hasattr(self, 'timeDelayfillingEntry'):
                        self.timeDelayfillingEntry.blockSignals(True)
                        self.timeDelayfillingEntry.setText(str(config.liquidVolumeTimeDelay))
                        self.timeDelayfillingEntry.blockSignals(False)
                        logger.info(f"    ✓ liquidVolumeTimeDelay: {config.liquidVolumeTimeDelay}")
                    
                    if hasattr(config, 'liquidTempTimeDelay') and hasattr(self, 'timeDelayTempEntry'):
                        self.timeDelayTempEntry.blockSignals(True)
                        self.timeDelayTempEntry.setText(str(config.liquidTempTimeDelay))
                        self.timeDelayTempEntry.blockSignals(False)
                        logger.info(f"    ✓ liquidTempTimeDelay: {config.liquidTempTimeDelay}")
>>>>>>> Stashed changes
                    
                    # Tank color
                    if hasattr(config, 'tankColor') and hasattr(self, 'colorDropDown'):
                        for i in range(self.colorDropDown.count()):
                            if self.colorDropDown.itemData(i) == config.tankColor:
                                self.colorDropDown.blockSignals(True)
                                self.colorDropDown.setCurrentIndex(i)
                                self.colorDropDown.blockSignals(False)
                                logger.info(f"    ✓ tankColor: {config.tankColor}")
<<<<<<< Updated upstream
                                count += 1
                                break
                    
                    # Display checkboxes
=======
                                break
                    
                    # CRITICAL: Display checkboxes
>>>>>>> Stashed changes
                    if hasattr(config, 'displayLevelSwitches') and hasattr(self, 'levelSwitchesCheckBox'):
                        self.levelSwitchesCheckBox.blockSignals(True)
                        self.levelSwitchesCheckBox.setChecked(config.displayLevelSwitches)
                        self.levelSwitchesCheckBox.blockSignals(False)
                        logger.info(f"    ✓ displayLevelSwitches: {config.displayLevelSwitches}")
<<<<<<< Updated upstream
                        count += 1
=======
>>>>>>> Stashed changes
                    
                    if hasattr(config, 'displayTemperature') and hasattr(self, 'analogValueTempCheckBox'):
                        self.analogValueTempCheckBox.blockSignals(True)
                        self.analogValueTempCheckBox.setChecked(config.displayTemperature)
                        self.analogValueTempCheckBox.blockSignals(False)
                        logger.info(f"    ✓ displayTemperature: {config.displayTemperature}")
<<<<<<< Updated upstream
                        count += 1
                    
                    logger.info(f">>> Config values applied: {count} fields updated")
=======
>>>>>>> Stashed changes
                    
                except Exception as e:
                    logger.error(f"Error applying config to GUI: {e}", exc_info=True)
            
            # SECTION 2: Apply status values to process displays
            if status:
                try:
<<<<<<< Updated upstream
                    count = 0
                    
=======
>>>>>>> Stashed changes
                    # Liquid parameters
                    if hasattr(status, 'liquidVolume') and hasattr(self, 'vat_widget'):
                        self.vat_widget.currentVolume = status.liquidVolume
                        logger.info(f"    ✓ liquidVolume: {status.liquidVolume:.2f} L")
<<<<<<< Updated upstream
                        count += 1
=======
>>>>>>> Stashed changes
                    
                    if hasattr(status, 'liquidTemperature') and hasattr(self, 'vat_widget'):
                        self.vat_widget.currentTemp = status.liquidTemperature
                        logger.info(f"    ✓ liquidTemperature: {status.liquidTemperature:.2f} °C")
<<<<<<< Updated upstream
                        count += 1
                    
                    logger.info(f">>> Status values applied: {count} fields updated")
=======
                    
                    # Valve positions
                    if hasattr(status, 'valveInOpenFraction') and hasattr(self, 'valveInEntry'):
                        valve_percent = int(status.valveInOpenFraction * 100)
                        self.valveInEntry.blockSignals(True)
                        self.valveInEntry.setText(str(valve_percent))
                        self.valveInEntry.blockSignals(False)
                        logger.info(f"    ✓ valveInOpenFraction: {status.valveInOpenFraction:.2f}")
                    
                    if hasattr(status, 'valveOutOpenFraction') and hasattr(self, 'valveOutEntry'):
                        valve_percent = int(status.valveOutOpenFraction * 100)
                        self.valveOutEntry.blockSignals(True)
                        self.valveOutEntry.setText(str(valve_percent))
                        self.valveOutEntry.blockSignals(False)
                        logger.info(f"    ✓ valveOutOpenFraction: {status.valveOutOpenFraction:.2f}")
                    
                    # Heater
                    if hasattr(status, 'heaterPowerFraction') and hasattr(self, 'heatingValueEntry'):
                        heater_percent = int(status.heaterPowerFraction * 100)
                        self.heatingValueEntry.blockSignals(True)
                        self.heatingValueEntry.setText(str(heater_percent))
                        self.heatingValueEntry.blockSignals(False)
                        logger.info(f"    ✓ heaterPowerFraction: {status.heaterPowerFraction:.2f}")
>>>>>>> Stashed changes
                    
                except Exception as e:
                    logger.error(f"Error applying status to GUI: {e}", exc_info=True)
            
            logger.info(">>> ✓ apply_loaded_state_to_gui completed successfully")
            
        except Exception as e:
<<<<<<< Updated upstream
            logger.error(f"ERROR in apply_loaded_state_to_gui: {e}", exc_info=True)
=======
            logger.error(f"ERROR in apply_loaded_state_to_gui: {e}", exc_info=True)
>>>>>>> Stashed changes
