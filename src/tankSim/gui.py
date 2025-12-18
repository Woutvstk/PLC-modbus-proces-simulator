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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize all configurable properties with defaults
        self._init_properties()
        
        # Load SVG file and setup rendering
        self._load_svg()
        
        # Create display widget
        self.renderer = QSvgRenderer()
        self.svg_widget = SvgDisplay(self.renderer)
        layout.addWidget(self.svg_widget)
        
        # Initial render
        self.rebuild()

<<<<<<< HEAD
    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def _init_properties(self):
        """Initialize all widget properties with default values"""
        # Flow and temperature
        self.toekomendDebiet = 0
        self.tempWeerstand = 20.0
        
        # Display options
        self.regelbareKleppen = False
        self.regelbareWeerstand = False
        self.niveauschakelaar = False
        self.analogeWaardeTemp = False
        
        # Actuator positions
        self.KlepStandBoven = 0
        self.KlepStandBeneden = 0
        
        # Visual settings
        self.kleurWater = Colors.BLUE
        self.controler = "GUI"
        
        # Internal SVG geometry
        self.waterInVat = None
        self.originalY = 0.0
        self.originalHoogte = 0.0
        self.maxHoogteGUI = 80
        self.ondersteY = 0.0
        
        # Configuration values (set from settings)
        self.valveInMaxFlowValue = 5
        self.valveOutMaxFlowValue = 2
        self.powerValue = 10000.0
        self.maxVolume = 200.0
=======
        # Default attribute values
        self.valveInMaxFlowValue = 0
        self.valveOutMaxFlowValue = 0
        self.powerValue = 10000.0
        self.adjustableValve = False
        self.adjustableHeatingCoil = False
        self.levelSwitches = False
        self.analogValueTemp = False
        self.adjustableValveInValue = 0
        self.adjustableValveOutValue = 0
        self.waterColor = blue
        self.controler = "GUI"
        self.maxVolume = 2.0
        self.levelSwitchMaxHeight = 90.0
        self.levelSwitchMinHeight = 10.0

        self.waterInVat = None
        self.originalY = 0.0
        self.originalHeight = 0.0
        self.maxheightGUI = 80
        self.lowestY = 0.0
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a

    def _load_svg(self):
        """Load and parse the SVG file"""
        try:
            svg_path = Path(__file__).parent.parent / "guiCommon" / "media" / "SVGVat.svg"
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
<<<<<<< HEAD
        visibility = "visible" if is_gui_mode else "hidden"
        
        if self.regelbareKleppen:
            self.visibility_group("regelbareKleppen", visibility)
        
        if self.regelbareWeerstand:
            self.visibility_group("regelbareweerstand", visibility)
        
        self.update_svg()
        self.svg_widget.update()

    # =========================================================================
    # PRIVATE METHODS - UPDATE SECTIONS
    # =========================================================================

    def _update_water_appearance(self):
        """Update water color in all relevant SVG elements"""
        self.set_group_color("waterTotaal", self.kleurWater)

    def _update_heater_status(self):
        """
        Update heater color based on temperature percentage.
        
        Temperature ranges:
        - 0-20%:   Gray (inactive)
        - 20-40%:  Green
        - 40-60%:  Blue
        - 60-80%:  Orange
        - 80-100%: Green
        - 100%+:   Red (overheating)
        """
        if self.tempWeerstand == 0:
            temp_percent = 0.0
        else:
            temp_percent = (tempVat * 100.0) / self.tempWeerstand
        
        temp_percent = max(0.0, min(100.0, temp_percent))
        
        # Determine color based on temperature range
        if temp_percent <= 20:
            color = Colors.GRAY
        elif temp_percent <= 40:
            color = Colors.GREEN
        elif temp_percent <= 60:
            color = Colors.BLUE
        elif temp_percent <= 80:
            color = Colors.ORANGE
        elif temp_percent < 100:
            color = Colors.GREEN
        else:
            color = Colors.RED
        
        self.set_group_color("warmteweerstand", color)

    def _update_valve_positions(self):
        """Update valve visuals based on current positions"""
        # Top valve
        if self.KlepStandBoven == 0:
            self.klep_breete("waterval", 0)
            self.set_group_color("KlepBoven", Colors.WHITE)
        else:
            self.klep_breete("waterval", self.KlepStandBoven)
            self.set_group_color("KlepBoven", self.kleurWater)
        
        # Bottom valve
        if self.KlepStandBeneden == 0:
            self.klep_breete("waterBeneden", 0)
            self.set_group_color("KlepBeneden", Colors.WHITE)
        else:
            self.klep_breete("waterBeneden", self.KlepStandBeneden)
            self.set_group_color("KlepBeneden", self.kleurWater)

    def _update_optional_displays(self):
        """Update visibility of optional display elements"""
        # Level switch
        if self.niveauschakelaar:
            self.visibility_group("niveauschakelaar", "visible")
        else:
            self.visibility_group("niveauschakelaar", "hidden")
        
        # Analog temperature display
        if self.analogeWaardeTemp:
            self.visibility_group("analogeWaardeTemp", "visible")
        else:
            self.visibility_group("analogeWaardeTemp", "hidden")

    def _update_controller_specific(self):
        """Update elements specific to controller type"""
        is_gui_mode = (self.controler == "GUI")
        
        # Analog valve controls
        if self.regelbareKleppen:
            visibility = "visible" if is_gui_mode else "hidden"
            self.visibility_group("regelbareKleppen", visibility)
        else:
            self.visibility_group("regelbareKleppen", "hidden")
        
        # Heater control
        if not self.regelbareWeerstand:
            self.visibility_group("regelbareweerstand", "hidden")
            # Digital heater - show on/off status
            if weerstand:
                self.set_group_color("weerstandStand", Colors.STATUS_OK)
            else:
                self.set_group_color("weerstandStand", Colors.STATUS_ERROR)
        else:
            visibility = "visible" if is_gui_mode else "hidden"
            self.visibility_group("regelbareweerstand", visibility)
=======
        visibility = "shown" if is_gui_mode else "hidden"

        if self.adjustableValve:
            self.visibilityGroup("adjustableValve", visibility)

        if self.adjustableHeatingCoil:
            self.visibilityGroup("adjustableHeatingCoil", visibility)

        self.updateSVG()
        self.svg_widget.update()

    def rebuild(self):
        """Complete rebuild of the SVG based on current values"""
        global liquidVolume

        self.setGroupColor("WaterGroup", self.waterColor)

        if self.powerValue == 0:
            tempVatProcent = 0.0
        else:
            tempVatProcent = (tempVat * 100.0) / self.powerValue

        tempVatProcent = max(0.0, min(100.0, tempVatProcent))

        match tempVatProcent:
            case x if 20 < x <= 40:
                self.setGroupColor("heatingCoil", green)
            case x if 40 < x <= 60:
                self.setGroupColor("heatingCoil", blue)
            case x if 60 < x <= 80:
                self.setGroupColor("heatingCoil", orange)
            case x if 80 < x < 100:
                self.setGroupColor("heatingCoil", green)
            case x if x >= 100:
                self.setGroupColor("heatingCoil", red)
            case _:
                self.setGroupColor("heatingCoil", "#808080")
        if self.levelSwitches:
            self.visibilityGroup("levelSwitchMax", "shown")
            self.visibilityGroup("levelSwitchMin", "shown")
        else:
            self.visibilityGroup("levelSwitchMax", "hidden")
            self.visibilityGroup("levelSwitchMin", "hidden")

        if self.analogValueTemp:
            self.visibilityGroup("analogValueTemp", "shown")
        else:
            self.visibilityGroup("analogValueTemp", "hidden")

        is_gui_mode = (self.controler == "GUI")

        if self.adjustableValve:
            visibility = "shown" if is_gui_mode else "hidden"
            self.visibilityGroup("adjustableValve", visibility)
        else:
            self.visibilityGroup("adjustableValve", "hidden")
        if not self.adjustableHeatingCoil:
            self.visibilityGroup("adjustableHeatingCoil", "hidden")
            if heatingCoil:
                self.setGroupColor("heatingCoilValue", green)
            elif not heatingCoil:
                self.setGroupColor("heatingCoilValue", red)
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

        if self.adjustableValveOutValue == 0:
            self.ValveWidth("waterValveOut", 0)
            self.setGroupColor("valveOut", "#FFFFFF")
        else:
            self.ValveWidth("waterValveOut", self.adjustableValveOutValue)
            self.setGroupColor("valveOut", self.waterColor)
        if tempVat == self.powerValue:
            self.setGroupColor("tempVat", green)
        else:
            self.setGroupColor("tempVat", red)

        self.setSVGText("adjustableValveInValue", str(
            self.adjustableValveInValue) + "%")
        self.setSVGText("adjustableValveOutValue", str(
            self.adjustableValveOutValue) + "%")
        self.setSVGText("valveInMaxFlowValue", str(
            self.valveInMaxFlowValue) + "l/s")
        self.setSVGText("valveOutMaxFlowValue", str(
            self.valveOutMaxFlowValue) + "l/s")
        self.setSVGText("levelSwitchMinHeight", str(
            self.levelSwitchMinHeight) + "%")
        self.setSVGText("levelSwitchMaxHeight", str(
            self.levelSwitchMaxHeight) + "%")
        self.setSVGText("powerValue",
                        str(self.powerValue) + "W")
        self.setSVGText("tempVatValue", str(tempVat) + "°C")
>>>>>>> ccd5c146433fbfe0fa7aa7ce20293ff44e10a43a

    def _update_text_displays(self):
        """Update all text values in the SVG"""
        self.set_svg_text("klepstandBoven", f"{self.KlepStandBoven}%")
        self.set_svg_text("KlepstandBeneden", f"{self.KlepStandBeneden}%")
        self.set_svg_text("debiet", f"{self.toekomendDebiet}l/s")
        self.set_svg_text("temperatuurWarmteweerstand", f"{self.tempWeerstand}°C")
        self.set_svg_text("temperatuurVatWaarde", f"{tempVat}°C")
        
        # Temperature indicator color
        if tempVat >= self.tempWeerstand:
            self.set_group_color("temperatuurVat", Colors.STATUS_OK)
        else:
            self.set_group_color("temperatuurVat", Colors.STATUS_ERROR)

<<<<<<< HEAD
    def _update_water_level(self):
        """Update water level visualization in the tank"""
        global currentHoogteVat, maxHoogteVat
        
        # Update level sensor status
        if currentHoogteVat >= maxHoogteVat:
            self.set_group_color("niveauschakelaar", Colors.STATUS_OK)
        else:
            self.set_group_color("niveauschakelaar", Colors.STATUS_ERROR)
        
        # Get water element reference
        if self.waterInVat is None:
            self.waterInVat = self.root.find(".//svg:*[@id='waterInVat']", self.ns)
            
            if self.waterInVat is not None:
                try:
                    self.originalY = float(self.waterInVat.get("y"))
                    self.originalHoogte = float(self.waterInVat.get("height"))
                except Exception:
                    self.originalY = 0.0
                    self.originalHoogte = 0.0
                
                self.maxHoogteGUI = 80
                self.ondersteY = self.originalY + self.originalHoogte
        
        # Update water level
        if self.waterInVat is not None:
            self._vat_vullen_GUI()

    def _vat_vullen_GUI(self):
        """Calculate and apply water fill level in the SVG"""
        global currentHoogteVat, maxHoogteVat
        
        # Calculate GUI height proportional to actual level
        hoogteVatGui = currentHoogteVat / maxHoogteVat * self.maxHoogteGUI
        nieuweY = self.ondersteY - hoogteVatGui
        
        # Update water rectangle
        if self.waterInVat is not None:
            self.waterInVat.set("height", str(hoogteVatGui))
            self.waterInVat.set("y", str(nieuweY))
        
        # Update level indicator
        self.set_hoogte_indicator("hoogteIndicator", nieuweY)
        self.set_hoogte_indicator("hoogteTekst", nieuweY + 2)
        self.set_svg_text("hoogteTekst", f"{int(currentHoogteVat)}mm")

    # =========================================================================
    # HELPER METHODS - SVG MANIPULATION
    # =========================================================================

    def set_hoogte_indicator(self, item_id, hoogte):
        """
        Set Y-position of an indicator element.
        
        Args:
            item_id: SVG element id
            hoogte: New Y position
        """
        item = self.root.find(f".//svg:*[@id='{item_id}']", self.ns)
        if item is not None:
            item.set("y", str(hoogte))

    def set_group_color(self, group_id, kleur):
        """
        Set fill color for all elements in an SVG group.
        
        Args:
            group_id: SVG group id
            kleur: Color (hex string, e.g., "#FF0000")
        """
        group = self.root.find(f".//svg:g[@id='{group_id}']", self.ns)
=======
        if self.waterInVat is not None:
            try:
                self.originalY = float(self.waterInVat.get("y"))
                self.originalHeight = float(self.waterInVat.get("height"))
            except Exception:
                self.originalY = 0.0
                self.originalHeight = 0.0

            self.lowestY = self.originalY + self.originalHeight
            self.LevelChangeVat()

        self.updateSVG()
        self.svg_widget.update()

    def updateSVG(self):
        """Update the renderer with the current SVG"""
        xml_bytes = ET.tostring(self.root, encoding="utf-8")
        self.renderer.load(xml_bytes)

    def LevelChangeVat(self):
        """Fill the tank based on liquidVolume"""
        global liquidVolume

        if liquidVolume/self.maxVolume >= self.levelSwitchMaxHeight:
            self.setGroupColor("levelSwitchMax", green)
        else:
            self.setGroupColor("levelSwitchMax", red)
        if liquidVolume/self.maxVolume >= self.levelSwitchMinHeight:
            self.setGroupColor("levelSwitchMin", green)
        else:
            self.setGroupColor("levelSwitchMin", red)

        realGUIHeight = liquidVolume/(self.maxVolume * 100) * self.maxheightGUI
        newY = self.lowestY - realGUIHeight

        if self.waterInVat is not None:
            self.waterInVat.set("height", str(realGUIHeight))
            self.waterInVat.set("y", str(newY))
        self.setHightIndicator("levelIndicator", newY)
        self.setHightIndicator("levelValue", newY + 2)
        self.setSVGText("levelValue", str(
            int(liquidVolume/self.maxVolume)) + "%")

    def setHightIndicator(self, itemId, hoogte):
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

<<<<<<< HEAD
    def visibility_group(self, group_id, visibility):
        """
        Set visibility of an SVG group.
        
        Args:
            group_id: SVG group id
            visibility: "visible" or "hidden"
        """
        group = self.root.find(f".//svg:g[@id='{group_id}']", self.ns)
        if group is not None:
            group.set("visibility", visibility)

    def klep_breete(self, item_id, klep_stand):
        """
        Adjust valve width based on position (0-100%).
        
        Args:
            item_id: SVG element id
            klep_stand: Valve position (0-100)
        """
        item = self.root.find(f".//svg:*[@id='{item_id}']", self.ns)
=======
    def visibilityGroup(self, groupId, visibility):
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

<<<<<<< HEAD
    def set_svg_text(self, item_id, value):
        """
        Set text content of an SVG text element.
        
        Args:
            item_id: SVG text element id
            value: New text value
        """
        item = self.root.find(f".//svg:*[@id='{item_id}']", self.ns)
=======
    def setSVGText(self, itemId, value):
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