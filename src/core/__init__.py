"""
Core module for Industrial Simulation Framework.

This module provides central configuration, protocol management,
and simulation orchestration capabilities.
"""

from .configuration import configuration
from .interface import SimulationInterface
from .simulationManager import SimulationManager
from .protocolManager import ProtocolManager

__all__ = [
    'configuration',
    'SimulationInterface',
    'SimulationManager',
    'ProtocolManager',
]
