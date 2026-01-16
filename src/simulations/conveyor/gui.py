import os
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QSize, QRectF
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter


class SvgDisplay(QWidget):
    """Widget that only renders the SVG."""

    def __init__(self, svg_path):
        super().__init__()
        self.renderer = QSvgRenderer()
        # Load SVG directly from file path
        if svg_path and Path(svg_path).exists():
            self.renderer.load(str(svg_path))
        
        # Set size policies to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(300, 200)

    def sizeHint(self):
        return QSize(600, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        svg_size = self.renderer.defaultSize()
        if svg_size.width() > 0 and svg_size.height() > 0:
            widget_rect = self.rect()
            svg_ratio = svg_size.width() / svg_size.height()
            widget_ratio = widget_rect.width() / widget_rect.height()

            if widget_ratio > svg_ratio:
                new_width = int(widget_rect.height() * svg_ratio)
                x_offset = (widget_rect.width() - new_width) // 2
                target_rect = widget_rect.adjusted(x_offset, 0, -x_offset, 0)
            else:
                new_height = int(widget_rect.width() / svg_ratio)
                y_offset = (widget_rect.height() - new_height) // 2
                target_rect = widget_rect.adjusted(0, y_offset, 0, -y_offset)

            target_rectf = QRectF(target_rect)
            self.renderer.render(painter, target_rectf)
        else:
            self.renderer.render(painter)


class ConveyorWidget(QWidget):
    """Widget for displaying conveyor belt simulation"""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set size policies to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Default attribute values
        self.conveyorSpeed = 0.0
        self.controler = "GUI"
        self.svg_path = None

        try:
            # Try multiple paths to find transportband.svg (handles different architectures)
            possible_paths = [
                Path(__file__).parent.parent.parent / "gui" / "media" / "transportband.svg",
                Path(__file__).parent.parent.parent / "gui" / "media" / "icon" / "transportband.svg",
                Path(__file__).parent.parent.parent / "gui" / "media" / "media" / "transportband.svg",
                Path(__file__).parent.parent.parent / "gui" / "media" / "media" / "icon" / "transportband.svg",
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.svg_path = path
                    break
            
            if self.svg_path is None:
                raise FileNotFoundError(f"SVG file not found in any of the expected locations: {possible_paths}")
        except Exception as e:
            raise RuntimeError("Cannot load 'transportband.svg': " + str(e))

        # Create SVG display widget
        self.svg_widget = SvgDisplay(self.svg_path)
        layout.addWidget(self.svg_widget, 1)

    def set_controller_mode(self, mode):
        """Set controller mode"""
        self.controler = mode

    def rebuild(self):
        """Rebuild the display"""
        if self.svg_widget:
            self.svg_widget.update()

    def update_speed(self, speed_value):
        """Update conveyor speed display"""
        self.conveyorSpeed = speed_value
        self.rebuild()
