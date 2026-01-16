import os
import xml.etree.ElementTree as ET
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QSize, QRectF
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter

# Colors
red = "#FF0000"
orange = "#FFA500"
blue = "#1100FF"
green = "#00FF00"

# Global variables

heatingCoil = True
liquidVolume = 0
tempVat = 0


class SvgDisplay(QWidget):
    """Widget that only renders the SVG."""

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer
        self.setMinimumSize(300, 350)
        self.setMaximumSize(1200, 1400)

    def sizeHint(self):
        return QSize(300, 350)

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


class VatWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Default attribute values
        self.valveInMaxFlowValue = 0
        self.valveOutMaxFlowValue = 0
        self.powerValue = 750.0
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
        self.heaterPowerFraction = 0.0

        self.waterInVat = None
        self.originalY = 0.0
        self.originalHeight = 0.0
        self.maxheightGUI = 85
        self.lowestY = 0.0

        try:
            # Try multiple paths to find SVGVat.svg (handles different architectures)
            possible_paths = [
                Path(__file__).parent.parent.parent /
                "gui" / "media" / "SVGVat.svg",
                Path(__file__).parent.parent /
                "guiCommon" / "media" / "SVGVat.svg",
                Path(__file__).parent.parent.parent /
                "gui" / "media" / "icon" / "SVG vat.svg",
                Path(__file__).parent.parent.parent /
                "guiCommon" / "media" / "SVGVat.svg",
            ]

            svg_path = None
            for path in possible_paths:
                if path.exists():
                    svg_path = path
                    break

            if svg_path is None:
                raise FileNotFoundError(
                    f"SVG file not found in any of the expected locations: {possible_paths}")

            self.svg_path = svg_path  # Store for later use
            self.tree = ET.parse(svg_path)
            self.root = self.tree.getroot()
            self.ns = {"svg": "http://www.w3.org/2000/svg"}
        except Exception as e:
            raise RuntimeError("Cannot load 'SVGVat.svg': " + str(e))

        self.renderer = QSvgRenderer()
        self.svg_widget = SvgDisplay(self.renderer)
        layout.addWidget(self.svg_widget)

        # Update SVG text elements with configured signal names
        self._update_svg_text_labels()

        self.rebuild()

    def _get_signal_names_from_io_config(self):
        """
        Get signal name customizations from IO configuration JSON.
        Returns a dict mapping default signal names to configured names.
        """
        signal_names = {}
        try:
            # Try to load the IO configuration JSON file
            io_json_path = Path(__file__).parent.parent.parent / \
                "IO" / "IO_configuration.json"

            if not io_json_path.exists():
                io_json_path = Path(__file__).parent.parent / \
                    "IO" / "IO_configuration.json"

            if io_json_path.exists():
                import json
                with open(io_json_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'signals' in config:
                        for signal in config['signals']:
                            if 'name' in signal:
                                signal_names[signal['name']] = signal['name']
        except Exception:
            pass

        return signal_names

    def _update_svg_text_labels(self):
        """
        Update SVG text elements with signal names from the IO configuration.
        Maps SVG text element IDs to their corresponding signal names.
        Checks both XML and JSON configuration files.
        """
        try:
            # Find the IO configuration file
            io_config_path = Path(__file__).parent.parent.parent / \
                "IO" / "IO_treeList_PIDtankValve.xml"

            if not io_config_path.exists():
                # Fallback: try alternative paths
                io_config_path = Path(__file__).parent.parent / \
                    "IO" / "IO_treeList_PIDtankValve.xml"

            if not io_config_path.exists():
                return  # Config file not found, skip text update

            # Load signal names from the XML
            tree = ET.parse(io_config_path)
            root = tree.getroot()

            # Mapping of SVG text element IDs to signal names in the config
            element_mapping = {
                'tagValveOut': 'ValveOut',
                'tagValveIn': 'ValveIn',
                'tagHeater': 'Heater',
                'tagTempValue': 'TemperatureSensor',
                'tagLevelSensor': 'LevelSensor',
                'tagLevelSwitchMax': 'LevelSensorHigh',
                'tagLevelSwitchMin': 'LevelSensorLow',
            }

            # Extract signal names from PIDtankValve section
            pid_tank = root.find('PIDtankValve')
            if pid_tank is None:
                return

            signal_names = {}

            # Get all signals from Inputs and Outputs
            for section in pid_tank.findall('.//Signal'):
                signal_name = section.text.strip() if section.text else ''
                if signal_name:
                    signal_names[signal_name] = signal_name

            # Also check JSON config for any customized names
            json_signal_names = self._get_signal_names_from_io_config()
            signal_names.update(json_signal_names)

            # Update SVG text elements with actual signal names
            for text_element_id, config_signal_name in element_mapping.items():
                # Get the signal name, prefer JSON config over XML, fallback to config_signal_name
                signal_name = signal_names.get(
                    config_signal_name, config_signal_name)

                # Find the text element by ID - search all elements with tag name 'text'
                # Try both with and without namespace
                found = False
                for text_elem in self.root.iter():
                    # Check if this is a text element (with or without namespace)
                    tag = text_elem.tag
                    if tag.endswith('text') or tag == 'text':
                        if text_elem.get('id') == text_element_id:
                            # Find tspan child and update text
                            for child in text_elem:
                                child_tag = child.tag
                                if child_tag.endswith('tspan') or child_tag == 'tspan':
                                    child.text = signal_name
                                    found = True
                                    break

                            # If no tspan found, update text directly
                            if not found:
                                text_elem.text = signal_name
                            break

            # Write updated SVG back to the file
            self.tree.write(str(self.svg_path),
                            encoding='utf-8', xml_declaration=True)

            # Reload the renderer with updated SVG
            self.renderer.load(str(self.svg_path))

        except Exception as e:
            # Silently fail if config cannot be loaded
            pass

    def update_tag_text_from_config(self, signal_config_mapping):
        """
        Update SVG tag text based on current IO configuration.
        Called when IO settings are modified.

        Args:
            signal_config_mapping: Dict mapping SVG element IDs to signal names
                Example: {'tagHeatingCoil': 'HeaterCustom', 'tagValueTemp': 'TempSensorCustom'}
        """
        try:
            # Mapping of SVG text element IDs to default signal names
            element_mapping = {
                'tagValveOut': 'ValveOut',
                'tagValveIn': 'ValveIn',
                'tagHeater': 'Heater',
                'tagTempValue': 'TemperatureSensor',
                'tagLevelSensor': 'LevelSensor',
                'tagLevelSwitchMax': 'LevelSensorHigh',
                'tagLevelSwitchMin': 'LevelSensorLow',
            }

            # Update SVG text elements with provided signal names
            for text_element_id, default_signal_name in element_mapping.items():
                signal_name = signal_config_mapping.get(
                    default_signal_name, default_signal_name)

                # Find the text element by ID - search all elements with tag name 'text'
                # Try both with and without namespace
                found = False
                for text_elem in self.root.iter():
                    # Check if this is a text element (with or without namespace)
                    tag = text_elem.tag
                    if tag.endswith('text') or tag == 'text':
                        if text_elem.get('id') == text_element_id:
                            # Find tspan child and update text
                            for child in text_elem:
                                child_tag = child.tag
                                if child_tag.endswith('tspan') or child_tag == 'tspan':
                                    child.text = signal_name
                                    found = True
                                    break

                            # If no tspan found, update text directly
                            if not found:
                                text_elem.text = signal_name
                            break

            # Write updated SVG back to the file
            self.tree.write(str(self.svg_path),
                            encoding='utf-8', xml_declaration=True)

            # Reload the renderer with updated SVG
            self.renderer.load(str(self.svg_path))

            # Refresh the widget display
            self.svg_widget.update()

        except Exception as e:
            # Silently fail if update cannot be performed
            pass

    def set_controller_mode(self, mode):
        """Set controller mode and update visibility of controls"""
        self.controler = mode
        self.updateControlsVisibility()

    def updateControlsVisibility(self):
        """Update visibility of GUI controls based on controller mode"""
        # Show analog indicators in both GUI and PLC modes so users can see live PLC values
        if self.adjustableValve:
            self.visibilityGroup("adjustableValve", "shown")

        if self.adjustableHeatingCoil:
            self.visibilityGroup("adjustableHeatingCoil", "shown")

        self.updateSVG()
        self.svg_widget.update()

    def updateControlsVisibility(self):
        """Update visibility of GUI controls based on controller mode"""
        # Show analog indicators in both GUI and PLC modes so users can see live PLC values
        if self.adjustableValve:
            self.visibilityGroup("adjustableValve", "shown")

        if self.adjustableHeatingCoil:
            self.visibilityGroup("adjustableHeatingCoil", "shown")

        self.updateSVG()
        self.svg_widget.update()

    def rebuild(self):
        """Complete rebuild of the SVG based on current values"""
        global liquidVolume

        self.setGroupColor("WaterGroup", self.waterColor)

        # Heating coil color: black (0%) → red (100%) based on heater power fraction (0.0-1.0)
        # 0.0 = black (#000000), 1.0 = full red (#FF0000)
        try:
            intensity = float(self.heaterPowerFraction)
        except Exception:
            intensity = 0.0

        # Clamp to 0.0..1.0 range
        intensity = max(0.0, min(1.0, intensity))

        # Convert to red channel 0..255, keep G=B=0
        red_val = int(round(255 * intensity))
        red_hex = f"#{red_val:02X}0000"
        self.setGroupColor("heatingCoil", red_hex)

        # Show max/min level switches only if the main level indicator is displayed
        # The main level indicator is always shown, but we check the levelSwitches flag
        if self.levelSwitches:
            self.visibilityGroup("levelSwitchMax", "shown")
            self.visibilityGroup("levelSwitchMin", "shown")
            self.visibilityGroup("tagLevelSwitchMax", "shown")
            self.visibilityGroup("tagLevelSwitchMin", "shown")
        else:
            self.visibilityGroup("levelSwitchMax", "hidden")
            self.visibilityGroup("levelSwitchMin", "hidden")
            self.visibilityGroup("tagLevelSwitchMax", "hidden")
            self.visibilityGroup("tagLevelSwitchMin", "hidden")

        # Always show the main level sensor tag regardless of switch visibility
        self.visibilityGroup("tagLevelSensor", "shown")

        if self.analogValueTemp:
            self.visibilityGroup("analogValueTemp", "shown")
        else:
            self.visibilityGroup("analogValueTemp", "hidden")

        # Always show analog valve indicators so PLC-driven values stay visible
        self.visibilityGroup("adjustableValve", "shown")
        if not self.adjustableHeatingCoil:
            self.visibilityGroup("adjustableHeatingCoil", "hidden")
            if heatingCoil:
                self.setGroupColor("heatingCoilValue", green)
            elif not heatingCoil:
                self.setGroupColor("heatingCoilValue", red)
            else:
                self.setGroupColor("heatingCoilValue", "#FFFFFF")
        else:
            # Keep visible even in PLC mode to reflect live heater power
            self.visibilityGroup("adjustableHeatingCoil", "shown")

        if self.adjustableValveInValue == 0:
            self.ValveWidth("waterValveIn", 0)
            self.setGroupColor("valveIn", "#FFFFFF")
        else:
            self.ValveWidth("waterValveIn", self.adjustableValveInValue)
            self.setGroupColor("valveIn", self.waterColor)

        if self.adjustableValveOutValue == 0 or liquidVolume <= 0:
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
        # Show tank water temperature with max 2 decimals
        try:
            self.setSVGText("tempVatValue", f"{float(tempVat):.2f}°C")
        except Exception:
            # Fallback to string conversion if formatting fails
            self.setSVGText("tempVatValue", str(tempVat) + "°C")

        self.waterInVat = self.root.find(
            f".//svg:*[@id='waterInVat']", self.ns)

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

        # Control water pipe visibility - show when there IS water in tank
        waterPipe = self.root.find(f".//svg:*[@id='waterPipe']", self.ns)
        if waterPipe is not None:
            if liquidVolume > 0:
                waterPipe.set("visibility", "visible")
            else:
                waterPipe.set("visibility", "hidden")

        # Control inlet water visibility - show when inlet valve is open
        waterValveIn = self.root.find(f".//svg:*[@id='waterValveIn']", self.ns)
        if waterValveIn is not None:
            if self.adjustableValveInValue > 0:
                waterValveIn.set("visibility", "visible")
                # Set the inlet water width based on actual flow
                if liquidVolume > 0:
                    # Normal case: tank has water, scale by inlet valve opening
                    self.ValveWidth(
                        "waterValveIn", self.adjustableValveInValue)
                else:
                    # No water in tank but inlet is open: scale by actual inlet flow
                    actual_flow = (self.adjustableValveInValue /
                                   100.0) * self.valveInMaxFlowValue
                    equivalent_inlet_opening = (
                        actual_flow / self.valveInMaxFlowValue) * 100.0
                    equivalent_inlet_opening = min(
                        100.0, equivalent_inlet_opening)
                    self.ValveWidth("waterValveIn", equivalent_inlet_opening)
            else:
                waterValveIn.set("visibility", "hidden")

        # Control outlet water visibility and width - show when:
        # 1. There IS water AND outlet valve is open, OR
        # 2. There is NO water AND BOTH inlet AND outlet valves are open (water through from inlet to outlet)
        waterValveOut = self.root.find(
            f".//svg:*[@id='waterValveOut']", self.ns)
        if waterValveOut is not None:
            if (liquidVolume > 0 and self.adjustableValveOutValue > 0) or \
               (liquidVolume <= 0 and self.adjustableValveInValue > 0 and self.adjustableValveOutValue > 0):
                # Set the outlet water width based on actual flow FIRST
                if liquidVolume > 0:
                    # Normal case: tank has water, scale by outlet valve opening
                    self.ValveWidth("waterValveOut",
                                    self.adjustableValveOutValue)
                else:
                    # No water in tank but both valves open: scale by actual inlet flow
                    # Actual flow = (inlet opening % × inlet max flow)
                    # Convert to equivalent outlet valve opening = (actual flow / outlet max flow) × 100
                    actual_flow = (self.adjustableValveInValue /
                                   100.0) * self.valveInMaxFlowValue
                    equivalent_outlet_opening = (
                        actual_flow / self.valveOutMaxFlowValue) * 100.0
                    # Cap at 100% to avoid overflow
                    equivalent_outlet_opening = min(
                        100.0, equivalent_outlet_opening)
                    self.ValveWidth("waterValveOut", equivalent_outlet_opening)

                # Then set visibility and color
                waterValveOut.set("visibility", "visible")
                waterValveOut.set("fill-opacity", "1")
                self.setGroupColor("valveOut", blue)
            else:
                waterValveOut.set("visibility", "hidden")
                waterValveOut.set("fill-opacity", "0")

        # Hide water height indicator when there is no water AND outgoing valve is open
        if liquidVolume <= 0 and self.adjustableValveOutValue > 0:
            self.visibilityGroup("levelValue", "hidden")
        else:
            self.visibilityGroup("levelValue", "shown")

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
            item.set("y", str(hoogte-3))

    def setGroupColor(self, groupId, kleur):
        """Set the color of an SVG group"""
        group = self.root.find(f".//svg:g[@id='{groupId}']", self.ns)
        if group is not None:
            for element in group:
                element.set("fill", kleur)

    def visibilityGroup(self, groupId, visibility):
        """Set the visibility of a group"""
        group = self.root.find(f".//svg:g[@id='{groupId}']", self.ns)
        if group is not None:
            group.set("visibility", visibility)

    def ValveWidth(self, itemId, KlepStand):
        """Adjust the width of a valve based on its position"""
        item = self.root.find(f".//svg:*[@id='{itemId}']", self.ns)
        if item is not None:
            new_width = (KlepStand * 0.0645)
            new_x = 105.745 - (KlepStand * 0.065) / 2
            item.set("width", str(new_width))
            item.set("x", str(new_x))

    def setSVGText(self, itemId, value):
        """Set the text of an SVG text element"""
        item = self.root.find(f".//svg:*[@id='{itemId}']", self.ns)
        if item is not None:
            tspan = item.find("svg:tspan", self.ns)
            if tspan is not None:
                tspan.text = value
            else:
                item.text = value

    def connect_pidvalve_controls(self):
        # Connect all new IO controls to the IO system
        # Flip-flop logic for Auto/Manual
        if hasattr(self, 'pushButton_PidValveAuto') and hasattr(self, 'pushButton_PidValveMan'):
            self.pushButton_PidValveAuto.setCheckable(True)
            self.pushButton_PidValveMan.setCheckable(True)
            self.pushButton_PidValveAuto.setChecked(True)  # Default to Auto
            self.pushButton_PidValveAuto.toggled.connect(
                lambda checked: self.pushButton_PidValveMan.setChecked(
                    not checked)
            )
            self.pushButton_PidValveMan.toggled.connect(
                lambda checked: self.pushButton_PidValveAuto.setChecked(
                    not checked)
            )
        # Connect digital buttons
        for btn_name in [
            'pushButton_PidValveStart', 'pushButton_PidValveStop',
            'radioButton_PidTankValveAItemp', 'radioButton_PidTankValveDItemp',
                'radioButton_PidTankValveAIlevel', 'radioButton_PidTankValveDIlevel']:
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setCheckable(True)
                # Optionally: connect to a slot to update IO state
        # Connect sliders to labels
        # Ensure slider value is always shown on label
        slider_temp = getattr(self, 'slider_PidTankTempSP', None)
        label_temp = getattr(self, 'label_PidTankTempSP', None)
        if slider_temp and label_temp:
            label_temp.setText(str(slider_temp.value()))
            slider_temp.valueChanged.connect(
                lambda val: label_temp.setText(str(val)))
        slider_level = getattr(self, 'slider_PidTankLevelSP', None)
        label_level = getattr(self, 'label_PidTankLevelSP', None)
        if slider_level and label_level:
            label_level.setText(str(slider_level.value()))
            slider_level.valueChanged.connect(
                lambda val: label_level.setText(str(val)))

    def set_plc_pidcontrol_index(self, gui_mode: bool):
        """Set PLCControl_PIDControl index: 0 for PLC, 1 for GUI."""
        # This assumes the parent or main window exposes these widgets
        parent = self.parent()
        # Try to find the PLCControl_PIDControl widget in the parent hierarchy
        plc_control = None
        w = self
        while w is not None:
            plc_control = getattr(w, 'PLCControl_PIDControl', None)
            if plc_control is not None:
                break
            w = getattr(w, 'parent', lambda: None)()
        if plc_control is not None:
            if gui_mode:
                plc_control.setCurrentIndex(1)
            else:
                plc_control.setCurrentIndex(0)
