"""
Uniform interface contract for all simulations.
All simulation classes must inherit from SimulationInterface.

Defines the standard API that all simulations must implement to ensure
consistency and enable the SimulationManager to work with any simulation type.

External Libraries Used:
- abc (Python Standard Library) - Abstract base class support
- typing (Python Standard Library) - Type hints for method signatures
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SimulationInterface(ABC):
    """Base class for all simulations ensuring uniform API."""
    
    @abstractmethod
    def start(self) -> None:
        """Start the simulation."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the simulation."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset simulation to initial state."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update simulation state.
        
        Args:
            dt: Time delta since last update in seconds
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status.
        
        Returns:
            Dictionary containing current simulation state
        """
        pass
    
    @abstractmethod
    def set_input(self, key: str, value: Any) -> None:
        """
        Set simulation input value.
        
        Args:
            key: Input parameter name
            value: Value to set
        """
        pass
    
    @abstractmethod
    def get_output(self, key: str) -> Any:
        """
        Get simulation output value.
        
        Args:
            key: Output parameter name
            
        Returns:
            Current value of the output
        """
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get simulation configuration.
        
        Returns:
            Dictionary containing current configuration
        """
        pass
    
    @abstractmethod
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Update simulation configuration.
        
        Args:
            config: Dictionary with configuration parameters to update
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get simulation name/identifier.
        
        Returns:
            Name of the simulation
        """
        pass
