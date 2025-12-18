"""
tankSim/gui.py - Tank Visualization Widget
===========================================

DEVELOPER GUIDE:
----------------
This file contains the visual representation of the tank simulation.
It uses SVG (Scalable Vector Graphics) for rendering.

STRUCTURE:
1. Global Configuration
2. VatWidget Class (main widget)
3. SVG Display Widget
4. Helper Methods

HOW TO ADD NEW VISUAL ELEMENTS:
1. Add element to SVGVat.svg with unique id
2. Add getter/setter property in VatWidget
3. Update rebuild() method to apply your changes
4. Add update logic to relevant section

DEPENDENCIES:
- SVGVat.svg (in guiCommon/media/)
- PyQt5 (QtWidgets, QtSvg, QtGui, QtCore)
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize, QRectF
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter


<<<<<<< HEAD
# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================
=======
# Global variables

heatingCoil = True
liquidVolume = 0
tempVat = 0
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a

# Color Palette
class Colors:
    """Predefined color constants for easy theming"""
    RED = "#FF0000"
    ORANGE = "#FFA500"
    BLUE = "#1100FF"
    GREEN = "#00FF00"
    YELLOW = "#FFFF00"
    PURPLE = "#800080"
    GRAY = "#808080"
    WHITE = "#FFFFFF"
    
    # Status colors
    STATUS_OK = GREEN
    STATUS_WARNING = ORANGE
    STATUS_ERROR = RED
    STATUS_INACTIVE = GRAY


# Global State Variables
# These are updated by the simulation and read by the GUI
maxHoogteVat = 200      # Maximum tank height (mm)
currentHoogteVat = 0    # Current liquid level (mm)
tempVat = 0             # Current temperature (°C)
weerstand = True        # Heater on/off state


# =============================================================================
# SVG DISPLAY WIDGET
# =============================================================================

class SvgDisplay(QWidget):
    """
    Widget that renders the SVG visualization.
    This is a separate widget to cleanly separate rendering from logic.
    """

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer
        self.setMinimumSize(300, 350)
        self.setMaximumSize(1200, 1400)

    def sizeHint(self):
        """Preferred size for the widget"""
        return QSize(300, 350)

    def paintEvent(self, event):
        """
        Qt paint event - called automatically when widget needs redrawing.
        Scales SVG to fit widget while maintaining aspect ratio.
        """
        painter = QPainter(self)
        svg_size = self.renderer.defaultSize()
        
        if svg_size.width() > 0 and svg_size.height() > 0:
            widget_rect = self.rect()
            svg_ratio = svg_size.width() / svg_size.height()
            widget_ratio = widget_rect.width() / widget_rect.height()

            # Center SVG in widget with correct aspect ratio
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


# =============================================================================
# MAIN VAT WIDGET CLASS
# =============================================================================

class VatWidget(QWidget):
    """
    Main tank visualization widget.
    
    USAGE:
    ------
    widget = VatWidget()
    widget.KlepStandBoven = 50  # Set top valve to 50%
    widget.rebuild()  # Apply changes and redraw
    
    PROPERTIES:
    -----------
    All properties are public and can be set directly:
    - toekomendDebiet: Incoming flow rate (l/s)
    - tempWeerstand: Heater temperature (°C)
    - regelbareKleppen: Use analog (0-100%) or digital valves
    - regelbareWeerstand: Use analog (0-100%) or digital heater
    - niveauschakelaar: Show level switch indicator
    - analogeWaardeTemp: Show analog temperature value
    - KlepStandBoven: Top valve position (0-100%)
    - KlepStandBeneden: Bottom valve position (0-100%)
    - kleurWater: Water color (hex string)
    - controler: Controller type ("GUI", "PLC", etc.)
    """

    def __init__(self):
        super().__init__()
        
        # Setup layout
        layout = QVBoxLayout(self)

        # Default attribute values
        self.toekomendDebiet = 0
        self.tempWeerstand = 20.0
        self.regelbareKleppen = False
        self.regelbareWeerstand = False
        self.niveauschakelaar = False
        self.analogeWaardeTemp = False
        self.KlepStandBoven = 0
        self.KlepStandBeneden = 0
        self.kleurWater = blue
        self.controler = "GUI"

        self.waterInVat = None
        self.originalY = 0.0
        self.originalHoogte = 0.0
        self.maxHoogteGUI = 80
        self.ondersteY = 0.0

        try:
            svg_path = Path(__file__).parent.parent / \
                "guiCommon" / "media" / "SVGVat.svg"
            self.tree = ET.parse(svg_path)
            self.root = self.tree.getroot()
            self.ns = {"svg": "http://www.w3.org/2000/svg"}
        except Exception as e:
            raise RuntimeError(f"Cannot load 'SVGVat.svg': {e}")

    # =========================================================================
    # PUBLIC API - MAIN METHODS
    # =========================================================================

    def rebuild(self):
        """
        Main method to rebuild the entire SVG visualization.
        Call this after changing any properties.
        
        FLOW:
        1. Update water appearance (color, level)
        2. Update heater status
        3. Update valve positions
        4. Update visibility of optional elements
        5. Update text displays
        6. Render updated SVG
        """
        global currentHoogteVat, tempVat
        
        # SECTION 1: Water Appearance
        self._update_water_appearance()
        
        # SECTION 2: Heater Status
        self._update_heater_status()
        
        # SECTION 3: Valve Positions
        self._update_valve_positions()
        
        # SECTION 4: Optional Display Elements
        self._update_optional_displays()
        
        # SECTION 5: Controller-specific Elements
        self._update_controller_specific()
        
        # SECTION 6: Text Displays
        self._update_text_displays()
        
        # SECTION 7: Water Level in Tank
        self._update_water_level()
        
        # SECTION 8: Final Render
        self.update_svg()
        self.svg_widget.update()

    def set_controller_mode(self, mode):
        """
        Set controller mode and update visibility of controls.
        
        Args:
            mode: "GUI", "PLC", "logo!", etc.
        """
        self.controler = mode
        self.updateControlsVisibility()

    def updateControlsVisibility(self):
        """Update visibility of GUI controls based on controller mode"""
        is_gui_mode = (self.controler == "GUI")
        visibility = "shown" if is_gui_mode else "hidden"

        if self.regelbareKleppen:
            self.visibility_group("regelbareKleppen", visibility)

        if self.regelbareWeerstand:
            self.visibility_group("regelbareweerstand", visibility)

        self.update_svg()
        self.svg_widget.update()

    def rebuild(self):
        """Complete rebuild of the SVG based on current values"""
        global currentHoogteVat, maxHoogteVat

        self.set_group_color("waterTotaal", self.kleurWater)

        if self.tempWeerstand == 0:
            tempVatProcent = 0.0
        else:
            tempVatProcent = (tempVat * 100.0) / self.tempWeerstand

        tempVatProcent = max(0.0, min(100.0, tempVatProcent))

        match tempVatProcent:
            case x if 20 < x <= 40:
                self.set_group_color("warmteweerstand", green)
            case x if 40 < x <= 60:
                self.set_group_color("warmteweerstand", blue)
            case x if 60 < x <= 80:
                self.set_group_color("warmteweerstand", orange)
            case x if 80 < x < 100:
                self.set_group_color("warmteweerstand", green)
            case x if x >= 100:
                self.set_group_color("warmteweerstand", red)
            case _:
                self.set_group_color("warmteweerstand", "#808080")

        if self.niveauschakelaar:
            self.visibility_group("niveauschakelaar", "shown")
        else:
            self.visibility_group("niveauschakelaar", "hidden")

        if self.analogeWaardeTemp:
            self.visibility_group("analogeWaardeTemp", "shown")
        else:
            self.visibilityGroup("analogValueTemp", "hidden")

    def _update_controller_specific(self):
        """Update elements specific to controller type"""
        is_gui_mode = (self.controler == "GUI")

        if self.regelbareKleppen:
            visibility = "shown" if is_gui_mode else "hidden"
            self.visibility_group("regelbareKleppen", visibility)
        else:
            self.visibility_group("regelbareKleppen", "hidden")

        if not self.regelbareWeerstand:
            self.visibility_group("regelbareweerstand", "hidden")
            if weerstand:
                self.set_group_color("weerstandStand", green)
            elif not weerstand:
                self.set_group_color("weerstandStand", red)
            else:
                self.setGroupColor("heatingCoilValue", "#FFFFFF")
        else:
            visibility = "shown" if is_gui_mode else "hidden"
            self.visibilityGroup("adjustableHeatingCoil", visibility)

        if self.adjustableValveInValue == 0:
            self.ValveWidth("waterValveIn", 0)
            self.setGroupColor("valveIn", "#FFFFFF")
        else:
            self.ValveWidth("waterValveIn", self.adjustableValveInValue)
            self.setGroupColor("valveIn", self.waterColor)

        if self.KlepStandBeneden == 0:
            self.klep_breete("waterBeneden", 0)
            self.set_group_color("KlepBeneden", "#FFFFFF")
        else:
            self.klep_breete("waterBeneden", self.KlepStandBeneden)
            self.set_group_color("KlepBeneden", self.kleurWater)

        if tempVat == self.tempWeerstand:
            self.set_group_color("temperatuurVat", green)
        else:
            self.set_group_color("temperatuurVat", red)

        self.set_svg_text("klepstandBoven", str(self.KlepStandBoven) + "%")
        self.set_svg_text("KlepstandBeneden", str(self.KlepStandBeneden) + "%")
        self.set_svg_text("debiet", str(self.toekomendDebiet) + "l/s")
        self.set_svg_text("temperatuurWarmteweerstand",
                          str(self.tempWeerstand) + "°C")
        self.set_svg_text("temperatuurVatWaarde", str(tempVat) + "°C")

        self.waterInVat = self.root.find(
            f".//svg:*[@id='waterInVat']", self.ns)

        if self.waterInVat is not None:
            try:
                self.originalY = float(self.waterInVat.get("y"))
                self.originalHoogte = float(self.waterInVat.get("height"))
            except Exception:
                self.originalY = 0.0
                self.originalHoogte = 0.0
            self.maxHoogteGUI = 80
            self.ondersteY = self.originalY + self.originalHoogte
            self.vat_vullen_GUI()

        self.update_svg()
        self.svg_widget.update()

    def update_svg(self):
        """Update the renderer with the current SVG"""
        xml_bytes = ET.tostring(self.root, encoding="utf-8")
        self.renderer.load(xml_bytes)

    def vat_vullen_GUI(self):
        """Fill the tank based on currentHoogteVat"""
        global currentHoogteVat, maxHoogteVat

        if currentHoogteVat >= maxHoogteVat:
            self.set_group_color("niveauschakelaar", green)
        else:
            self.set_group_color("niveauschakelaar", red)

        hoogteVatGui = currentHoogteVat / maxHoogteVat * self.maxHoogteGUI
        nieuweY = self.ondersteY - hoogteVatGui

        if self.waterInVat is not None:
            self.waterInVat.set("height", str(hoogteVatGui))
            self.waterInVat.set("y", str(nieuweY))

        self.set_hoogte_indicator("hoogteIndicator", nieuweY)
        self.set_hoogte_indicator("hoogteTekst", nieuweY + 2)
        self.set_svg_text("hoogteTekst", str(int(currentHoogteVat)) + "mm")

    def set_hoogte_indicator(self, itemId, hoogte):
        """Set the Y-position of an indicator"""
        item = self.root.find(f".//svg:*[@id='{itemId}']", self.ns)
        if item is not None:
            item.set("y", str(hoogte))

    def setGroupColor(self, groupId, kleur):
        """Set the color of an SVG group"""
        group = self.root.find(f".//svg:g[@id='{groupId}']", self.ns)
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a
        if group is not None:
            for element in group:
                element.set("fill", kleur)

    def visibility_group(self, groupId, visibility):
        """Set the visibility of a group"""
        group = self.root.find(f".//svg:g[@id='{groupId}']", self.ns)
        if group is not None:
            group.set("visibility", visibility)

    def ValveWidth(self, itemId, KlepStand):
        """Adjust the width of a valve based on its position"""
        item = self.root.find(f".//svg:*[@id='{itemId}']", self.ns)
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a
        if item is not None:
            new_width = klep_stand * 0.0645
            new_x = 105.745 - (klep_stand * 0.065) / 2
            item.set("width", str(new_width))
            item.set("x", str(new_x))

    def set_svg_text(self, itemId, value):
        """Set the text of an SVG text element"""
        item = self.root.find(f".//svg:*[@id='{itemId}']", self.ns)
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a
        if item is not None:
            tspan = item.find("svg:tspan", self.ns)
            if tspan is not None:
                tspan.text = value
            else:
                item.text = value

    def update_svg(self):
        """Convert XML tree to bytes and reload renderer"""
        xml_bytes = ET.tostring(self.root, encoding="utf-8")
        self.renderer.load(xml_bytes)


# =============================================================================
# DEVELOPER NOTES
# =============================================================================

"""
ADDING NEW VISUAL ELEMENTS:
---------------------------

1. Edit SVGVat.svg in Inkscape or text editor:
   - Add new element with unique id
   - Example: <rect id="myNewElement" x="10" y="10" width="50" height="20"/>

2. Add property to VatWidget.__init__():
   self.myNewProperty = False

3. Add update logic in rebuild():
   def _update_my_new_element(self):
       if self.myNewProperty:
           self.set_group_color("myNewElement", Colors.GREEN)
       else:
           self.set_group_color("myNewElement", Colors.RED)
   
   Then call it in rebuild():
   self._update_my_new_element()

4. Use from main code:
   widget.myNewProperty = True
   widget.rebuild()

AVAILABLE SVG METHODS:
---------------------
- set_group_color(id, color) - Change color
- visibility_group(id, "visible"/"hidden") - Show/hide
- set_svg_text(id, text) - Change text
- set_hoogte_indicator(id, y_pos) - Move element vertically
- klep_breete(id, percentage) - Adjust valve width

COLOR CONSTANTS:
---------------
Use Colors.RED, Colors.GREEN, etc. for consistency.
Or define new colors: Colors.MY_COLOR = "#AABBCC"
"""