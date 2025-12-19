# Dynamic Tree List Implementation

## Overview

Implemented dynamic loading of IO tree configuration based on the active simulation. Each simulation now has its own dedicated treeList XML file.

## Files Created

### 1. `src/IO/treeList_PIDtankValve.xml`

- Configuration for the PID Tank Valve simulation
- Includes GeneralControls (always present)
- Includes PIDtankValve-specific signals:
  - Digital Inputs: LevelSensorHigh, LevelSensorLow
  - Analog Inputs: LevelSensor, TemperatureSensor
  - Digital Outputs: ValveIn, ValveOut, Heater
  - Analog Outputs: ValveInFraction, ValveOutFraction, HeaterFraction

### 2. `src/IO/treeList_conveyor.xml`

- Configuration for the Conveyor Simulation (ready for future development)
- Includes GeneralControls (always present)
- Includes ConveyorSim-specific signals:
  - Digital Inputs: MotorRunning, EmergencyStop, ProductDetected
  - Analog Inputs: ConveyorSpeed, ProductCount
  - Digital Outputs: MotorStart, MotorStop, ResetCounter
  - Analog Outputs: SpeedSetpoint, AccelerationRate

## Code Changes

### `src/gui/ioConfigPage.py`

#### Updated `load_io_tree()` method

- Now dynamically determines active simulation using `simulationManager.get_active_simulation_name()`
- Loads the appropriate treeList XML file based on active simulation:
  - `treeList_PIDtankValve.xml` for PIDtankValve simulation
  - `treeList_conveyor.xml` for conveyor simulation
  - Falls back to `IO_treeList.xml` if no simulation is active
- Always loads GeneralControls signals first
- Maintains backward compatibility with old format

#### Added `_load_simulation_signals()` method

- Generic method to load any simulation's signals
- Parameters: `sim_element` (XML element), `sim_name` (display name)
- Handles both Inputs and Outputs sections
- Can be reused for any future simulations

### `src/gui/mainGui.py`

#### Updated `go_to_io()` method

- Now automatically reloads the IO tree when navigating to the IO page
- Uses `io_settings_mixin.load_io_tree()` to refresh with the active simulation's configuration
- Includes error handling for graceful fallback

## Architecture Benefits

1. **Scalability**: Easy to add new simulations by creating new treeList XML files
2. **Maintainability**: Each simulation has its own dedicated configuration
3. **Dynamic Loading**: Tree updates automatically when simulation changes
4. **Backward Compatibility**: Old format still supported as fallback
5. **Centralized**: All IO definitions remain in src/IO directory

## Usage

When users switch between simulations:

1. The simulation becomes active in SimulationManager
2. When they navigate to the IO page, the appropriate tree is automatically loaded
3. Only signals relevant to that simulation are shown
4. GeneralControls are always available

## Files Available

- `src/IO/IO_treeList.xml` (legacy, fallback)
- `src/IO/treeList_PIDtankValve.xml` (NEW)
- `src/IO/treeList_conveyor.xml` (NEW)
