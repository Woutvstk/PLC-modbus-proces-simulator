"""
Trend Display Module for PID Tank Valve Simulation
Displays historical data with PV, Setpoint, and OP (Output)
Includes pause, zoom, scroll, and hover tooltip features
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from collections import deque
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class TrendData:
    """Stores and manages trend data"""

    def __init__(self, name, max_points=5000):
        self.name = name
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.setpoints = deque(maxlen=max_points)
        self.outputs = deque(maxlen=max_points)  # OP - controller output
        self.start_time = None

    def add_point(self, value, setpoint=None, output=None):
        """Add a new data point with optional setpoint and output"""
        if self.start_time is None:
            self.start_time = datetime.now()

        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.timestamps.append(elapsed)
        self.values.append(value)
        self.setpoints.append(setpoint if setpoint is not None else value)
        self.outputs.append(output if output is not None else 0)

    def clear(self):
        """Clear all data"""
        self.timestamps.clear()
        self.values.clear()
        self.setpoints.clear()
        self.outputs.clear()
        self.start_time = None

    def get_data(self):
        """Return timestamps, values, setpoints, and outputs as lists"""
        return list(self.timestamps), list(self.values), list(self.setpoints), list(self.outputs)


class SingleTrendDisplay(QWidget):
    """Standalone trend display window with PV, Setpoint, and OP graphs"""

    def __init__(self, trend_name, unit, color='blue', parent=None):
        super().__init__(parent)
        self.trend_name = trend_name
        self.unit = unit
        self.color = color
        self.is_paused = False
        self.is_running = True

        self.setWindowTitle(f"Trend Monitor - {trend_name}")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize trend data
        self.trend_data = TrendData(f"{trend_name} ({unit})")

        # For hover annotations and value persistence
        self.annotation = None
        self.last_annotation_time = None

        # For custom zoom - track user-defined X-axis range
        self.custom_x_range = None  # Store (width, left_edge) when user zooms

        # Create UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Minimize margins
        main_layout.setSpacing(2)  # Minimize spacing between elements

        # Title - smaller and more compact
        title = QLabel(f"{self.trend_name} Trend Monitor")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setMaximumHeight(20)
        main_layout.addWidget(title)

        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        # Add navigation toolbar for zoom and pan with minimal height
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setMaximumHeight(25)
        main_layout.addWidget(self.toolbar)

        # Add stretch factor to maximize canvas
        main_layout.addWidget(self.canvas, 1)

        # Connect mouse events for hover tooltip
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('axes_leave_event', self.on_mouse_leave)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)
        button_layout.setSpacing(5)

        # Left arrow button to pan left
        left_arrow_btn = QPushButton("← Left")
        left_arrow_btn.setMinimumHeight(35)
        left_arrow_btn.clicked.connect(self.pan_left)
        left_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        button_layout.addWidget(left_arrow_btn)

        # Right arrow button to pan right
        right_arrow_btn = QPushButton("Right →")
        right_arrow_btn.setMinimumHeight(35)
        right_arrow_btn.clicked.connect(self.pan_right)
        right_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        button_layout.addWidget(right_arrow_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setMinimumHeight(35)
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #FF9800;
            }
        """)
        button_layout.addWidget(self.pause_btn)

        clear_btn = QPushButton("Clear Trend")
        clear_btn.setMinimumHeight(35)
        clear_btn.clicked.connect(self.clear_trend)
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        button_layout.addWidget(clear_btn)

        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

        # Initialize plot
        self.ax = None
        self._setup_plot()

        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def showEvent(self, event):
        """Called when window is shown - set focus for keyboard events"""
        super().showEvent(event)
        self.setFocus()
        self.activateWindow()

    def _setup_plot(self):
        """Setup the matplotlib plot"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(
            f"{self.trend_name} - PV, Setpoint & OP", fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Time (seconds)", fontsize=10)
        self.ax.set_ylabel(f"{self.trend_name} ({self.unit})", fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_facecolor('#f8f8f8')

        # Remove existing annotation if any
        if self.annotation:
            self.annotation.remove()
            self.annotation = None

        self.figure.tight_layout()
        self.canvas.draw()

    def toggle_pause(self, checked):
        """Toggle pause state"""
        self.is_paused = checked
        if checked:
            self.pause_btn.setText("Resume")
        else:
            self.pause_btn.setText("Pause")

    def keyPressEvent(self, event):
        """Handle keyboard events for arrow keys"""
        if not event.isAutoRepeat():  # Only handle new key presses, not repeats
            if event.key() == Qt.Key_Left:
                # Left arrow key - pan left
                self.pan_left()
            elif event.key() == Qt.Key_Right:
                # Right arrow key - pan right
                self.pan_right()
            else:
                # Pass other key events to parent
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def set_simulation_running(self, running):
        """Set whether simulation is running"""
        self.is_running = running

    def update_data(self, pv_value, setpoint_value=None, output_value=None):
        """Update trend data with PV, setpoint, and output"""
        # Only add data if not paused and simulation is running
        if not self.is_paused and self.is_running:
            self.trend_data.add_point(pv_value, setpoint_value, output_value)

    def refresh_plot(self):
        """Refresh the plot with current data"""
        if not self.ax:
            return

        # Get data
        times, pv_values, sp_values, op_values = self.trend_data.get_data()

        # Clear and redraw
        self.ax.clear()

        # Plot PV (Process Variable) - RED
        if times and pv_values:
            self.ax.plot(times, pv_values, color='#FF0000', linewidth=2.5,
                         linestyle='-', label='PV (Process Value)', alpha=0.9, zorder=3)

        # Plot Setpoint - BLUE (no area fill)
        if times and sp_values:
            self.ax.plot(times, sp_values, color='#0000FF', linewidth=2.5,
                         linestyle='-', label='Setpoint', alpha=0.9, zorder=2, marker=None)

        # Plot OP (Output) - GREEN
        if times and op_values:
            self.ax.plot(times, op_values, color='#00AA00', linewidth=2,
                         linestyle='-', label='Output power', alpha=0.8, zorder=2)

        self.ax.set_title(f"{self.trend_name} - PV, Setpoint & OP",
                          fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Time (seconds)", fontsize=10)
        self.ax.set_ylabel(f"Value ({self.unit})", fontsize=10)

        # Set Y-axis range to 0-100%
        self.ax.set_ylim(0, 100)

        # Auto-scrolling X-axis with 180-second window (or custom zoom if set)
        if times:
            import matplotlib.ticker as ticker
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))

            current_time = times[-1]

            # Use custom zoom range if user has set it
            if self.custom_x_range:
                width, left_edge = self.custom_x_range
                # Use the stored left edge and width
                self.ax.set_xlim(left_edge, left_edge + width)
                # Adjust x-axis interval based on zoom level
                self._adjust_x_axis_interval(width)
            else:
                # Default 180-second window that scrolls as time progresses
                if current_time > 180:
                    self.ax.set_xlim(current_time - 180, current_time)
                else:
                    self.ax.set_xlim(0, 180)
                # Use default 20-second intervals
                import matplotlib.ticker as ticker
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))

        self.ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax.set_facecolor('#f8f8f8')
        self.ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

        self.figure.tight_layout(pad=0.5)
        self.canvas.draw_idle()

    def on_mouse_move(self, event):
        """Show tooltip on mouse hover - only when paused"""
        if not self.is_paused:
            # Hide annotation when not paused
            if self.annotation:
                try:
                    self.annotation.remove()
                    self.annotation = None
                    self.canvas.draw_idle()
                except:
                    pass
            return

        if event.inaxes != self.ax:
            return

        try:
            times, pv_values, sp_values, op_values = self.trend_data.get_data()
            if not times:
                return

            # Find closest data point
            x_mouse = event.xdata
            y_mouse = event.ydata

            # Find index of closest time
            distances = [abs(t - x_mouse) for t in times]
            min_idx = distances.index(min(distances))

            time_val = times[min_idx]
            pv_val = pv_values[min_idx]
            sp_val = sp_values[min_idx]
            op_val = op_values[min_idx]

            # Create annotation text
            text = f"Time: {time_val:.2f}s\nPV: {pv_val:.2f} {self.unit}\nSP: {sp_val:.2f} {self.unit}\nOP: {op_val:.1f}%"

            try:
                self.annotation = self.ax.annotate(
                    text,
                    xy=(time_val, pv_val),
                    xytext=(15, -15),
                    textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.8', fc='white',
                              alpha=0.95, ec='#333333', lw=2),
                    fontsize=10,
                    fontweight='bold',
                    zorder=100
                )
                self.canvas.draw_idle()
            except Exception as e:
                pass
        except Exception as e:
            pass

    def on_mouse_leave(self, event):
        """Keep annotation visible for a bit after mouse leaves (persistence)"""
        pass  # Keep showing the last annotation for a bit

    def _adjust_x_axis_interval(self, width):
        """Adjust x-axis tick interval based on zoom level"""
        import matplotlib.ticker as ticker

        # Choose interval based on width to show reasonable number of ticks
        if width < 40:
            interval = 5  # 5-second intervals
        elif width < 80:
            interval = 10  # 10-second intervals
        elif width < 120:
            interval = 20  # 20-second intervals
        elif width < 300:
            interval = 30  # 30-second intervals
        else:
            interval = 60  # 60-second intervals

        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(interval))

    def on_scroll(self, event):
        """Handle mouse wheel scroll to zoom X-axis in/out - left edge stays fixed"""
        if event.inaxes != self.ax:
            return

        try:
            # Get current X-axis limits
            cur_xlim = self.ax.get_xlim()
            left_edge = cur_xlim[0]  # Keep left edge fixed
            xdata = cur_xlim[1] - cur_xlim[0]

            # Zoom factor: scroll up = zoom in (shorter range), scroll down = zoom out (larger range)
            if event.button == 'up':
                # Zoom in - reduce range by 10%
                scale_factor = 0.9
            else:  # 'down'
                # Zoom out - increase range by 10%
                scale_factor = 1.1

            new_width = xdata * scale_factor

            # Get data and keep limits reasonable
            times, _, _, _ = self.trend_data.get_data()
            current_time = times[-1] if times else 0
            if times:
                max_range = max(times[-1], 180) if times else 180
                new_width = max(10, min(new_width, max_range))

            # Keep left edge fixed, extend right edge
            new_right = left_edge + new_width

            # Store width and left edge
            self.custom_x_range = (new_width, left_edge)

            # Set new limits with left edge fixed
            self.ax.set_xlim([left_edge, new_right])

            self.canvas.draw_idle()
        except Exception as e:
            pass

    def zoom_in(self):
        """Zoom in on the plot"""
        try:
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            xdata = cur_xlim[1] - cur_xlim[0]
            ydata = cur_ylim[1] - cur_ylim[0]
            self.ax.set_xlim([cur_xlim[0] + xdata * 0.2,
                             cur_xlim[1] - xdata * 0.2])
            self.ax.set_ylim([cur_ylim[0] + ydata * 0.2,
                             cur_ylim[1] - ydata * 0.2])
            self.canvas.draw_idle()
        except:
            pass

    def zoom_out(self):
        """Zoom out on the plot"""
        try:
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            xdata = cur_xlim[1] - cur_xlim[0]
            ydata = cur_ylim[1] - cur_ylim[0]
            self.ax.set_xlim([cur_xlim[0] - xdata * 0.2,
                             cur_xlim[1] + xdata * 0.2])
            self.ax.set_ylim([cur_ylim[0] - ydata * 0.2,
                             cur_ylim[1] + ydata * 0.2])
            self.canvas.draw_idle()
        except:
            pass

    def pan_left(self):
        """Pan the view to the left (move backward in time) - keeps zoom level constant"""
        try:
            cur_xlim = self.ax.get_xlim()
            width = cur_xlim[1] - cur_xlim[0]  # Keep the zoom width constant

            # Pan left by 50% of current view width for faster navigation
            pan_amount = width * 0.5

            # Calculate new position
            new_left = cur_xlim[0] - pan_amount
            new_right = new_left + width  # Keep same width

            # Don't go before time 0
            if new_left < 0:
                new_left = 0
                new_right = width

            # Store the current zoom width and new position in custom_x_range
            self.custom_x_range = (width, new_left)

            self.ax.set_xlim([new_left, new_right])
            self.canvas.draw_idle()
        except:
            pass

    def pan_right(self):
        """Pan the view to the right (move forward in time) - keeps zoom level constant"""
        try:
            cur_xlim = self.ax.get_xlim()
            width = cur_xlim[1] - cur_xlim[0]  # Keep the zoom width constant

            # Get the latest time from data
            times, _, _, _ = self.trend_data.get_data()
            current_time = times[-1] if times else 0

            # Pan right by 50% of current view width for faster navigation
            pan_amount = width * 0.5

            # Calculate new position
            new_left = cur_xlim[0] + pan_amount
            new_right = new_left + width  # Keep same width

            # Don't go beyond current time
            if new_right > current_time:
                new_right = current_time
                new_left = new_right - width

            # Don't go before time 0
            if new_left < 0:
                new_left = 0
                new_right = width

            # Store the current zoom width and new position in custom_x_range
            self.custom_x_range = (width, new_left)

            self.ax.set_xlim([new_left, new_right])
            self.canvas.draw_idle()
        except:
            pass

    def clear_trend(self):
        """Clear all trend data"""
        self.trend_data.clear()
        if self.annotation:
            try:
                self.annotation.remove()
                self.annotation = None
            except:
                pass
        self.custom_x_range = None
        self.refresh_plot()

    def closeEvent(self, event):
        """Handle window close event - just close this window, don't affect simulation"""
        event.accept()


class LevelTrendDisplay(SingleTrendDisplay):
    """Level trend display with different color scheme"""

    def refresh_plot(self):
        """Refresh the plot with current data - Level specific colors"""
        if not self.ax:
            return

        # Get data
        times, pv_values, sp_values, op_values = self.trend_data.get_data()

        # Clear and redraw
        self.ax.clear()

        # Plot PV (Process Variable) - GREEN
        if times and pv_values:
            self.ax.plot(times, pv_values, color='#00AA00', linewidth=2.5,
                         linestyle='-', label='PV (Process Value)', alpha=0.9, zorder=3)

        # Plot Setpoint - BLUE (no area fill)
        if times and sp_values:
            self.ax.plot(times, sp_values, color='#0000FF', linewidth=2.5,
                         linestyle='-', label='Setpoint', alpha=0.9, zorder=2, marker=None)

        # Plot OP (Output) - RED
        if times and op_values:
            self.ax.plot(times, op_values, color='#FF0000', linewidth=2,
                         linestyle='-', label='Output power', alpha=0.8, zorder=2)

        self.ax.set_title(f"{self.trend_name} - PV, Setpoint & OP",
                          fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Time (seconds)", fontsize=10)
        self.ax.set_ylabel(f"Value ({self.unit})", fontsize=10)

        # Set Y-axis range to 0-100%
        self.ax.set_ylim(0, 100)

        # Auto-scrolling X-axis with 180-second window (or custom zoom if set)
        if times:
            import matplotlib.ticker as ticker
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))

            current_time = times[-1]

            # Use custom zoom range if user has set it
            if self.custom_x_range:
                width, left_edge = self.custom_x_range
                # Use the stored left edge and width
                self.ax.set_xlim(left_edge, left_edge + width)
                # Adjust x-axis interval based on zoom level
                self._adjust_x_axis_interval(width)
            else:
                # Default 180-second window that scrolls as time progresses
                if current_time > 180:
                    self.ax.set_xlim(current_time - 180, current_time)
                else:
                    self.ax.set_xlim(0, 180)
                # Use default 20-second intervals
                import matplotlib.ticker as ticker
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(20))

        self.ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax.set_facecolor('#f8f8f8')
        self.ax.legend(loc='upper left', fontsize=9, framealpha=0.95)

        self.figure.tight_layout(pad=0.5)
        self.canvas.draw_idle()
