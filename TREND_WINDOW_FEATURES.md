# Trend Window Features Update

## Overview
Enhanced the trend display windows with new features for better control and window management.

## New Features

### 1. **Axis Range Controls**
Added input fields to the trend window to manually control X-axis (time) and Y-axis (value) ranges:

- **X-axis Range**: Two input fields (min/max in seconds) to set the time window
  - Default: 0 to 180 seconds
  - Allows zooming into specific time periods
  - Can be adjusted while the simulation is running

- **Y-axis Range**: Two input fields (min/max values) to set the value range
  - Default: 0 to 100 (adjustable per unit type)
  - Allows focusing on specific value ranges
  - Independent of the data being displayed

**How to Use:**
1. Open a trend window (Temperature or Level Trend)
2. You'll see axis range controls at the bottom of the plot area
3. Enter desired min/max values for each axis
4. The plot updates automatically

### 2. **Window Docking System**
Trend windows can now be docked together or separated:

- **Docking**: When you drag a trend window close to another trend window, they automatically dock together in the same window group
- **Undocking**: Click and drag outside the plot area and release to undock the window from a group
- **Window Groups**: Multiple trend windows can be managed as a group for synchronized operations

**How to Use:**
1. Open multiple trend windows (Temperature and Level)
2. Drag one window to another to dock them
3. Click and drag outside the plot area (on the frame) to undock
4. Undocked windows appear as separate floating windows

### 3. **Synchronized Axis Ranges**
When trend windows are docked together:
- Changing the axis range in one window updates all other docked windows
- Helps maintain consistent views across multiple trends
- Can be manually overridden per window

## Technical Implementation

### Modified Classes and Methods

**TrendWindowGroup**
- New class to manage groups of docked trend windows
- Tracks which windows belong to the same group
- Supports merging and separating window groups

**SingleTrendDisplay** (now inherits from QMainWindow)
- Changed from QWidget to QMainWindow to support proper window management
- Added axis range spinbox widgets
- Added docking/undocking event handlers
- New methods:
  - `_on_x_range_changed()`: Handle X-axis range changes
  - `_on_y_range_changed()`: Handle Y-axis range changes
  - `_check_for_undock()`: Detect undocking gestures
  - `_dock_with_other_window()`: Dock with another window
  - `_sync_axis_ranges()`: Synchronize ranges across docked windows
  - `_on_canvas_press/release/motion()`: Handle mouse events for dragging

**LevelTrendDisplay**
- Updated `refresh_plot()` to use axis range spinbox values

**UI Improvements**
- Added compact axis range control row between toolbar and buttons
- Input fields validate min/max values automatically
- Responsive design that scales with window size

## Files Modified
- `src/simulations/PIDtankValve/trendDisplay.py` - Main implementation

## Backward Compatibility
- Existing trend window functionality remains unchanged
- New features are additive and don't break existing code
- Windows default to previous behavior if controls not used
