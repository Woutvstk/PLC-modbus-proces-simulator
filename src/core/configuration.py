"""
Central Configuration Module.

This module provides:
- Initial application state loading on startup
- Save/Load complete simulation states via simulationManager
- Centralized config access for all modules
"""
import csv
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .simulationManager import SimulationManager

logger = logging.getLogger(__name__)


class configuration:
    """
    Main configuration class for the application.
    Manages PLC connection settings and application state.
    """

    def __init__(self):
        """Constructor: create configuration object with default parameters"""
        
        # Control process through gui or plc
        self.plcGuiControl = "plc"  # options: gui/plc
        self.doExit = False
        
        # PLC connection settings
        # Options: "Gui", "PLC S7-1500/1200/400/300/ET 200SP", "PLC S7-300/400", 
        #          "logo!", "PLCSim S7-1500 advanced", "PLCSim S7-1500/1200/400/300/ET 200SP"
        self.plcProtocol: str = "PLC S7-1500/1200/400/300/ET 200SP"
        self.plcIpAdress: str = "192.168.0.1"
        self.plcPort: int = 502  # ModBusTCP default port
        self.plcRack: int = 0
        self.plcSlot: int = 1
        self.tsapLogo: int = 0x0300  # CLIENT(sim) SIDE
        self.tsapServer: int = 0x0200  # LOGO SIDE
        
        # Set True by gui, set False by main
        self.tryConnect: bool = False
        
        # Variables to export/import
        self.importExportVariableList = [
            "plcGuiControl", "plcProtocol",
            "plcIpAdress", "plcPort", "plcRack", "plcSlot", 
            "tsapLogo", "tsapServer"
        ]
    
    def saveToFile(self, exportFileName: str, createFile: bool = False) -> bool:
        """
        Save configuration to a CSV file.
        
        Args:
            exportFileName: Path to the export file
            createFile: If True, creates new file; if False, appends to existing
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            logger.info(f"Exporting config to: {exportFileName}")
            openMode: str = "w" if createFile else "a"
            
            with open(exportFileName, openMode, newline="") as file:
                writer = csv.writer(file)
                if createFile:
                    # Add CSV header for new file
                    writer.writerow(["variable", "value"])
                
                # Write all variables from list with value to CSV
                for variable in self.importExportVariableList:
                    writer.writerow([variable, getattr(self, variable)])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config to {exportFileName}: {e}")
            return False
    
    def loadFromFile(self, importFileName: str) -> bool:
        """
        Load configuration from a CSV file.
        
        Args:
            importFileName: Path to the import file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(importFileName, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    for variable in self.importExportVariableList:
                        if row["variable"] == variable:
                            # Convert to correct type based on current attribute type
                            current_type = type(getattr(self, variable))
                            setattr(self, variable, current_type(row["value"]))
            
            logger.info(f"Config loaded from: {importFileName}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config from {importFileName}: {e}")
            return False
    
    def Save(self, simulation_manager: Optional['SimulationManager'], 
             export_filename: str) -> bool:
        """
        Save complete application state including simulation state.
        
        Args:
            simulation_manager: SimulationManager instance to save simulation state
            export_filename: Path to save the complete state
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Save main configuration
            if not self.saveToFile(export_filename, createFile=True):
                return False
            
            # Save simulation state if manager is provided and has active simulation
            if simulation_manager:
                active_sim = simulation_manager.get_active_simulation()
                sim_name = simulation_manager.get_active_simulation_name()
                
                if active_sim and sim_name:
                    # Get simulation status and save it
                    status = simulation_manager.get_status()
                    if status and hasattr(active_sim, 'get_status_object'):
                        status_obj = active_sim.get_status_object()
                        if hasattr(status_obj, 'saveToFile'):
                            status_obj.saveToFile(export_filename, createFile=False)
                    
                    # Get simulation config and save it
                    config = simulation_manager.get_config()
                    if config and hasattr(active_sim, 'get_config_object'):
                        config_obj = active_sim.get_config_object()
                        if hasattr(config_obj, 'saveToFile'):
                            config_obj.saveToFile(export_filename, createFile=False)
                    
                    logger.info(f"Saved simulation state for: {sim_name}")
            
            logger.info(f"Complete state saved to: {export_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save complete state: {e}")
            return False
    
    def Load(self, simulation_manager: Optional['SimulationManager'], 
             import_filename: str) -> bool:
        """
        Load complete application state including simulation state.
        
        Args:
            simulation_manager: SimulationManager instance to load simulation state
            import_filename: Path to load the complete state from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load main configuration
            if not self.loadFromFile(import_filename):
                return False
            
            # Load simulation state if manager is provided and has active simulation
            if simulation_manager:
                active_sim = simulation_manager.get_active_simulation()
                sim_name = simulation_manager.get_active_simulation_name()
                
                if active_sim and sim_name:
                    # Load simulation status
                    if hasattr(active_sim, 'get_status_object'):
                        status_obj = active_sim.get_status_object()
                        if hasattr(status_obj, 'loadFromFile'):
                            status_obj.loadFromFile(import_filename)
                    
                    # Load simulation config
                    if hasattr(active_sim, 'get_config_object'):
                        config_obj = active_sim.get_config_object()
                        if hasattr(config_obj, 'loadFromFile'):
                            config_obj.loadFromFile(import_filename)
                    
                    logger.info(f"Loaded simulation state for: {sim_name}")
            
            logger.info(f"Complete state loaded from: {import_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load complete state: {e}")
            return False
