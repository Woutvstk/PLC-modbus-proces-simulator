import csv


class statusClass:
    def __init__(self):
        # valve IN status
        # written by: plc, gui or import
        self.valveInOpenFraction: float = 0

        # valve OUT status
        # written by: plc, gui or import
        self.valveOutOpenFraction: float = 0

        # heating element status
        # written by: plc, gui or import
        self.heaterPowerFraction: float = 0

        # digital level sensor status
        # written by: procesSim
        self.digitalLevelSensorLowTriggered: bool = False
        self.digitalLevelSensorHighTriggered: bool = False

        # liquid parameters
        # written by: procesSim, import
        self.liquidVolume = 100
        # initialize liquid temp
        # written by: procesSim, import
        self.liquidTemperature = 0

        # simulation status
        # written by: gui
        self.simRunning = False

        # flow rates
        # written by process
        self.flowRateIn = 0
        self.flowRateOut = 0

    # Save config to a CSV file
    def saveToFile(self, exportFileName, createFile: bool = False):
        print(f"Exporting status to: {exportFileName}")
        openMode: str
        if (createFile):
            openMode = "w"  # if creating new file, open in Write mode
        else:
            openMode = "a"  # if adding to existing file, open in append mode

        with open(exportFileName, openMode, newline="") as file:
            writer = csv.writer(file)
            if (createFile):
                # if creating new file, add csv header first
                writer.writerow(["variable", "value"])
            writer.writerow(["valveInOpenFraction", self.valveInOpenFraction])
            writer.writerow(["heaterPowerFraction", self.heaterPowerFraction])
            writer.writerow(["liquidVolume", self.liquidVolume])
            file.close

    # Read status back from the CSV file
    def loadFromFile(self, importFileName: str):
        with open(importFileName, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["variable"] == "valveInOpenFraction":
                    self.valveInOpenFraction = float(row["value"])
                elif row["variable"] == "heaterPowerFraction":
                    self.heaterPowerFraction = float(row["value"])
                elif row["variable"] == "liquidVolume":
                    self.liquidVolume = float(row["value"])
        print(f"Status loaded from: {importFileName}")
