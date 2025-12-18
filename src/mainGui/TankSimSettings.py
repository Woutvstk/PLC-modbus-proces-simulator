# tankSimSettingsPage.py - Tank Simulation Specific Settings
# REFACTORED: Now uses interface.py for all logic

from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Import the interface
from tankSim.SVGinterface import TankSimInterface


class TankSimSettingsMixin:
    """
    Mixin class for tank simulation GUI setup
    All logic is delegated to TankSimInterface
    """

    def init_tanksim_settings_page(self):
        """Initialize tank simulation page components"""
        # Create interface
        self.tanksim_interface = TankSimInterface(self)
        self.tanksim_interface.initialize()
        
        # Setup GUI elements
        self._init_color_dropdown()
        self._init_checkboxes()
        self._init_entry_fields()
        self._init_simulation_button()
        self._init_apply_button()
        
        # Initialize stacked widget to settings page
        try:
            self.stackedWidget_SimSettings.setCurrentIndex(0)
        except AttributeError:
            pass

    # GUI setup methods remain unchanged
    def _init_color_dropdown(self):
        """Initialize water color dropdown"""
        try:
            self.kleurDropDown.clear()
            colors = [
                ("Blue", "#0000FF"),
                ("Red", "#FB5C5C"),
                ("Green", "#00FF00"),
                ("Yellow", "#FAFA2B"),
                ("Orange", "#FFB52B"),
                ("Purple", "#800080"),
                ("Gray", "#808080"),
            ]
            for name, hexcode in colors:
                self.kleurDropDown.addItem(name, hexcode)
            
            self.kleurDropDown.currentIndexChanged.connect(self.on_kleur_changed)
        except AttributeError:
            pass

    def _init_checkboxes(self):
        """Connect all tank-specific checkboxes"""
        try:
            self.regelbareKlepenCheckBox.toggled.connect(self.on_tank_config_changed)
            self.regelbareWeerstandCheckBox.toggled.connect(self.on_tank_config_changed)
            self.niveauschakelaarCheckBox.toggled.connect(self.on_tank_config_changed)
            self.analogeWaardeTempCheckBox.toggled.connect(self.on_tank_config_changed)
        except AttributeError:
            pass

    def _init_entry_fields(self):
        """Synchronize entry fields"""
        try:
            self.entryGroupDebiet = [
                self.toekomendDebietEntry,
                self.toekomendDebietEntry1,
                self.toekomendDebietEntry2
            ]
            self.entryGroupTemp = [
                self.tempWeerstandEntry,
                self.tempWeerstandEntry1
            ]

            for group in (self.entryGroupDebiet, self.entryGroupTemp):
                for field in group:
                    field.textChanged.connect(
                        lambda text, g=group: self.syncFields(text, g))
        except AttributeError:
            pass

    def _init_simulation_button(self):
        """Initialize simulation start/stop button"""
        try:
            self.pushButton_startSimulatie.setCheckable(True)
            self.pushButton_startSimulatie.toggled.connect(self.toggle_simulation)
            self.pushButton_startSimulatie.setText("START SIMULATIE")
            self.pushButton_startSimulatie.setStyleSheet("""
                QPushButton {
                    background-color: #44FF44;
                    color: black;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00CC00;
                }
            """)
        except AttributeError:
            pass
    
    def _init_apply_button(self):
        """Connect apply button"""
        try:
            self.pushButton_applyPIDValveSettings.clicked.connect(
                self.apply_tanksim_settings)
        except AttributeError:
            pass

    # =========================================================================
    # DELEGATION TO INTERFACE
    # =========================================================================
    
    def update_tanksim_display(self):
        """Delegate to interface"""
        if hasattr(self, 'tanksim_interface'):
            self.tanksim_interface.update(
                self.tanksim_config, 
                self.tanksim_status
            )
    
    def write_gui_values_to_status(self):
        """Delegate to interface"""
        if hasattr(self, 'tanksim_interface'):
            self.tanksim_interface.write_gui_to_status(self.tanksim_status)
    
    def apply_tanksim_settings(self):
        """Called when user clicks Apply button"""
        if hasattr(self, 'tanksim_interface'):
            self.tanksim_interface.write_gui_to_config(self.tanksim_config)

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_kleur_changed(self):
        """Color changed - handled by update loop"""
        pass

    def on_tank_config_changed(self):
        """Config changed - handled by update loop"""
        pass

    def syncFields(self, text, group):
        """Synchronize linked entry fields"""
        for field in group:
            if field.text() != text:
                field.blockSignals(True)
                field.setText(text)
                field.blockSignals(False)

    def toggle_simulation(self, checked):
        """Toggle simulation on/off"""
        if checked:
            if hasattr(self, 'tanksim_status') and self.tanksim_status:
                self.tanksim_status.simRunning = True
                
            self.pushButton_startSimulatie.setText("STOP SIMULATIE")
            self.pushButton_startSimulatie.setStyleSheet("""
                QPushButton {
                    background-color: #FF4444;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #CC0000;
                }
            """)
        else:
            if hasattr(self, 'tanksim_status') and self.tanksim_status:
                self.tanksim_status.simRunning = False
                
            self.pushButton_startSimulatie.setText("START SIMULATIE")
            self.pushButton_startSimulatie.setStyleSheet("""
                QPushButton {
                    background-color: #44FF44;
                    color: black;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00CC00;
                }
            """)