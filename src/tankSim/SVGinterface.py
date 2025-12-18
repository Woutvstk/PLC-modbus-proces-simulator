"""
tankSim/interface.py - Tank Simulation Interface Layer
Centralized interface between GUI and tank simulation
All tank-specific GUI logic lives here
"""

from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from tankSim.gui import VatWidget
import tankSim.gui as gui_module


class TankSimInterface:
    """
    Central interface for tank simulation
    Manages all communication between GUI, visualization, and simulation
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.vat_widget = None
        
        # Cache for entry widgets (initialized later)
        self.entry_widgets = {}
        
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def initialize(self):
        """Initialize the interface - call this after main window is fully loaded"""
        self._create_vat_widget()
        self._cache_entry_widgets()
    
    def _create_vat_widget(self):
        """Create and embed VatWidget in the GUI"""
        try:
            self.vat_widget = VatWidget()
            container = self.main_window.findChild(QWidget, "vatWidgetContainer")
            
            if container:
                existing_layout = container.layout()
                if existing_layout is None:
                    container_layout = QVBoxLayout(container)
                    container_layout.setContentsMargins(0, 0, 0, 0)
                else:
                    container_layout = existing_layout
                    container_layout.setContentsMargins(0, 0, 0, 0)
                
                container_layout.addWidget(self.vat_widget)
        except Exception as e:
            print(f"⚠️ Could not create VatWidget: {e}")
    
    def _cache_entry_widgets(self):
        """Cache references to all entry widgets for fast access"""
        widget_names = [
            'maxFlowInEntry', 'maxFlowOutEntry', 'powerHeatingCoilEntry',
            'volumeEntry', 'levelSwitchMaxHeightEntry', 'levelSwitchMinHeightEntry',
            'timeDelayFillingEntry', 'ambientTempEntry', 'heatLossVatEntry',
            'timeDelayTempEntry', 'specificHeatCapacityEntry', 'specificWeightEntry',
            'boilingTempEntry', 'klepstandBovenEntry', 'klepstandBenedenEntry'
        ]
        
        for name in widget_names:
            widget = getattr(self.main_window, name, None)
            if widget:
                self.entry_widgets[name] = widget
    
    # =========================================================================
    # UPDATE LOOP - Called every frame
    # =========================================================================
    
    def update(self, config, status):
        """
        Main update loop - called from MainWindow timer
        
        DATAFLOW:
        1. Read status → Update global variables for SVG
        2. Read GUI → Update VatWidget properties
        3. Rebuild SVG
        """
        if not config or not status:
            return
        
        # Step 1: Update global SVG variables from simulation status
        gui_module.currentHoogteVat = status.liquidVolume
        gui_module.tempVat = status.liquidTemperature
        
        # Step 2: Update VatWidget from GUI inputs
        self._update_vat_widget_from_gui(config)
        
        # Step 3: Update GUI panels visibility
        self._update_gui_panel_visibility()
        
        # Step 4: Read valve positions from GUI
        self._read_valve_positions_from_gui()
        
        # Step 5: Rebuild SVG
        if self.vat_widget:
            self.vat_widget.rebuild()
    
    def _update_vat_widget_from_gui(self, config):
        """Update VatWidget properties from GUI entry fields"""
        if not self.vat_widget:
            return
        
        # Flow rates
        self.vat_widget.toekomendDebiet = self._get_entry_value('maxFlowInEntry', 200)
        self.vat_widget.tempWeerstand = self._get_entry_value('powerHeatingCoilEntry', 20.0)
        
        # Max values from config
        self.vat_widget.valveInMaxFlowValue = config.valveInMaxFlow
        self.vat_widget.valveOutMaxFlowValue = config.valveOutMaxFlow
        self.vat_widget.powerValue = config.heaterMaxPower
        self.vat_widget.maxVolume = config.tankVolume
        
        # Checkboxes
        try:
            self.vat_widget.regelbareKleppen = self.main_window.regelbareKlepenCheckBox.isChecked()
            self.vat_widget.regelbareWeerstand = self.main_window.regelbareWeerstandCheckBox.isChecked()
            self.vat_widget.niveauschakelaar = self.main_window.niveauschakelaarCheckBox.isChecked()
            self.vat_widget.analogeWaardeTemp = self.main_window.analogeWaardeTempCheckBox.isChecked()
        except AttributeError:
            pass
        
        # Water color
        try:
            self.vat_widget.kleurWater = self.main_window.kleurDropDown.currentData()
        except AttributeError:
            pass
        
        # Controller mode
        if hasattr(self.main_window, 'mainConfig') and self.main_window.mainConfig:
            self.vat_widget.controler = self.main_window.mainConfig.plcProtocol
    
    def _update_gui_panel_visibility(self):
        """Show/hide GUI control panels based on controller mode"""
        try:
            is_gui_mode = (hasattr(self.main_window, 'mainConfig') and 
                          self.main_window.mainConfig and 
                          self.main_window.mainConfig.plcGuiControl == "gui")
            
            if is_gui_mode and self.vat_widget.regelbareKleppen:
                if not self.main_window.regelbareKlepenGUISim.isVisible():
                    self.main_window.GUiSim.hide()
                    self.main_window.regelbareKlepenGUISim.show()
            elif is_gui_mode and not self.vat_widget.regelbareKleppen:
                if not self.main_window.GUiSim.isVisible():
                    self.main_window.regelbareKlepenGUISim.hide()
                    self.main_window.GUiSim.show()
            else:
                if self.main_window.GUiSim.isVisible() or self.main_window.regelbareKlepenGUISim.isVisible():
                    self.main_window.GUiSim.hide()
                    self.main_window.regelbareKlepenGUISim.hide()
        except AttributeError:
            pass
    
    def _read_valve_positions_from_gui(self):
        """Read valve positions from GUI controls and update VatWidget"""
        if not self.vat_widget:
            return
        
        if self.vat_widget.regelbareKleppen:
            # Analog control (0-100%)
            self.vat_widget.KlepStandBoven = self._get_entry_value('klepstandBovenEntry', 0)
            self.vat_widget.KlepStandBeneden = self._get_entry_value('klepstandBenedenEntry', 0)
        else:
            # Digital control (ON/OFF)
            try:
                top_checked = self.main_window.klepstandBovenCheckBox.isChecked()
                bottom_checked = self.main_window.klepstandBenedenCheckBox.isChecked()
                self.vat_widget.KlepStandBoven = 100 if top_checked else 0
                self.vat_widget.KlepStandBeneden = 100 if bottom_checked else 0
            except AttributeError:
                pass
    
    # =========================================================================
    # WRITE TO SIMULATION - GUI → Status
    # =========================================================================
    
    def write_gui_to_status(self, status):
        """
        Write GUI actuator positions to simulation status
        Only in GUI mode!
        """
        if not hasattr(self.main_window, 'mainConfig') or not self.main_window.mainConfig:
            return
        
        if self.main_window.mainConfig.plcGuiControl != "gui":
            return
        
        if not self.vat_widget:
            return
        
        # Write valve positions
        status.valveInOpenFraction = self.vat_widget.KlepStandBoven / 100.0
        status.valveOutOpenFraction = self.vat_widget.KlepStandBeneden / 100.0
        
        # Write heater
        if self.vat_widget.regelbareWeerstand:
            status.heaterPowerFraction = 0.5  # Placeholder
        else:
            try:
                heater_on = self.main_window.weerstandCheckBox.isChecked()
                status.heaterPowerFraction = 1.0 if heater_on else 0.0
            except AttributeError:
                status.heaterPowerFraction = 0.0
    
    # =========================================================================
    # WRITE TO CONFIG - Apply Settings
    # =========================================================================
    
    def write_gui_to_config(self, config):
        """
        Write GUI settings to simulation config
        Called when user clicks "Apply Settings"
        """
        config.valveInMaxFlow = self._get_entry_value('maxFlowInEntry', 5.0)
        config.valveOutMaxFlow = self._get_entry_value('maxFlowOutEntry', 2.0)
        config.heaterMaxPower = self._get_entry_value('powerHeatingCoilEntry', 10000.0)
        config.tankVolume = self._get_entry_value('volumeEntry', 200.0)
        
        config.digitalLevelSensorHighTriggerLevel = self._get_entry_value(
            'levelSwitchMaxHeightEntry', 180.0)
        config.digitalLevelSensorLowTriggerLevel = self._get_entry_value(
            'levelSwitchMinHeightEntry', 20.0)
        
        config.liquidVolumeTimeDelay = self._get_entry_value('timeDelayFillingEntry', 0.0)
        config.ambientTemp = self._get_entry_value('ambientTempEntry', 21.0)
        config.tankHeatLoss = self._get_entry_value('heatLossVatEntry', 150.0)
        config.liquidTempTimeDelay = self._get_entry_value('timeDelayTempEntry', 0.0)
        config.liquidSpecificHeatCapacity = self._get_entry_value('specificHeatCapacityEntry', 4186.0)
        config.liquidSpecificWeight = self._get_entry_value('specificWeightEntry', 0.997)
        config.liquidBoilingTemp = self._get_entry_value('boilingTempEntry', 100.0)
        
        print("✅ Settings applied to config!")
        print(f"   - Tank volume: {config.tankVolume} L")
        print(f"   - Max flow in: {config.valveInMaxFlow} L/s")
        print(f"   - Max flow out: {config.valveOutMaxFlow} L/s")
        print(f"   - Heater power: {config.heaterMaxPower} W")
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_entry_value(self, widget_name, default):
        """Safely get value from entry widget with default fallback"""
        try:
            widget = self.entry_widgets.get(widget_name)
            if widget and widget.text():
                return type(default)(widget.text())
            return default
        except (ValueError, AttributeError):
            return default