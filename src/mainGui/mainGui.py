from tkinter import filedialog
import tkinter as tk
import pathlib
import os
from PIL import Image, ImageTk
import math

# import class definition of mainConfig
from configuration import configuration as mainConfigClass


# kept for text color, autocomplete, ... TODO: change to base class
from tankSim.status import status as tankSimStatusClass
from tankSim.configuration import configuration as tankSimConfigurationClass


# tankSim specific imports
from tankSim.gui import process as tankSimProcessScreenClass
from tankSim.gui import settings as tankSimSettingsScreenClass

navColor = '#383838'

defaultMainConfig: mainConfigClass = mainConfigClass()


# flag to notify the rest of the program that the gui has been closed
exitProgram = False
TryConnectPending = False
importCommand: bool = False
exportCommand: bool = False


ip_adress = defaultMainConfig.plcIpAdress
SaveControler = "PLC S7-1500/1200/400/300"

# TODO change to base class
currenScreen: tankSimProcessScreenClass = None


def getAbsolutePath(relativePath: str) -> str:
    current_dir = pathlib.Path(__file__).parent.resolve()
    return os.path.join(current_dir, relativePath)


class MainScherm:
    def __init__(main, root):
        conColor = '#383838'
        main.root = root
        main.root.title("PID Regelaar Tank")
        main.root.geometry("1200x700")
        main.root.configure(bg="white")

        main.conFrame = tk.Frame(main.root, bg=conColor, height=45)
        main.conFrame.place(relwidth=1.0, x=50, y=4)

        connectButton = tk.Button(main.conFrame, text="Connect",
                                  bg=conColor, activebackground=conColor, fg="white", command=main.setTryConnect)
        connectButton.place(x=830, y=10)

        main.AdresLabel = tk.Label(main.conFrame, text="IP Adress:",
                                   bg=conColor, fg="White", font=("Arial", 10))
        main.AdresLabel.place(x=900, y=10)
        main.Adres = tk.Entry(main.conFrame, bg=conColor,
                              fg="White", font=("Arial", 10))
        main.Adres.place(x=970, y=12.5)
        main.Adres.insert(0, ip_adress)

        main.MainFrame = tk.Frame(main.root, bg="white")
        main.MainFrame.place(relwidth=1.0, relheight=1.0, x=50, y=50)

    def setTryConnect(self):
        global TryConnectPending, ip_adress
        ip_adress = self.Adres.get()
        TryConnectPending = True


class NavigationFrame:
    def __init__(nav, root, MainFrame):
        global currenScreen
        navColor = '#383838'
        nav = tk.Frame(root, bg=navColor)
        nav.pack(side="left", fill=tk.Y, padx=3, pady=4)
        nav.pack_propagate(flag=False)
        nav.configure(width=45)

        def navMenuAnimatie():
            current_width = nav.winfo_width()
            if current_width < 200:
                current_width += 10
                nav.config(width=current_width)
                root.after(ms=8, func=navMenuAnimatie)

        def navMenuAnimatieClose():
            current_width = nav.winfo_width()
            if current_width != 45:
                current_width -= 10
                nav.config(width=current_width)
                root.after(ms=8, func=navMenuAnimatieClose)

        def navMenuOpen():
            navMenuAnimatie()
            toggleNav.config(text="Close", command=navMenuClose)
            HomeText = tk.Label(nav, text="Home", bg=navColor, fg="white")
            HomeText.place(x=45, y=140)
            HomeText.bind("<Button-1>", lambda e: welkePagina(home_indicator,
                          tankSimProcessScreenClass, MainFrame))

            SettingsText = tk.Label(
                nav, text="Settings", bg=navColor, fg="white")
            SettingsText.place(x=45, y=200)
            SettingsText.bind("<Button-1>", lambda e: welkePagina(
                settings_indicator, tankSimSettingsScreenClass, MainFrame))

            mainSettingsText = tk.Label(
                nav, text="mainSettings", bg=navColor, fg="white")
            mainSettingsText.place(x=45, y=260)
            mainSettingsText.bind("<Button-1>", lambda e: welkePagina(
                mainSettings_indicator, tankSimSettingsScreenClass, MainFrame))

        def navMenuClose():
            navMenuAnimatieClose()
            toggleNav.config(text="nav", command=navMenuOpen)

        toggleNav = tk.Button(nav, text="Nav", bg=navColor,
                              bd=0, activebackground=navColor, command=navMenuOpen)
        toggleNav.place(x=4, y=10, width=40, height=40)

        home = tk.Button(nav, text="Home", bg=navColor,
                         bd=0, activebackground=navColor, command=lambda: welkePagina(home_indicator, tankSimProcessScreenClass, MainFrame))
        home.place(x=4, y=130, width=40, height=40)
        home_indicator = tk.Label(nav, bg=navColor)
        home_indicator.place(x=3, y=130, width=3, height=40)

        settings = tk.Button(nav, text="Settings",
                             bg=navColor, bd=0, activebackground=navColor, command=lambda: welkePagina(settings_indicator, tankSimSettingsScreenClass, MainFrame))
        settings.place(x=4, y=190, width=40, height=40)
        settings_indicator = tk.Label(nav, bg=navColor)
        settings_indicator.place(x=3, y=190, width=3, height=40)

        mainSettings = tk.Button(nav, text="mainSettings", bg=navColor,
                                 bd=0, activebackground=navColor, command=lambda: welkePagina(mainSettings_indicator, mainSettingsScreenClass, MainFrame))
        mainSettings.place(x=4, y=250, width=40, height=40)
        mainSettings_indicator = tk.Label(nav, bg=navColor)
        mainSettings_indicator.place(x=3, y=250, width=3, height=40)

        def welkePagina(indicator_lb, page, MainFrame):
            global currenScreen
            home_indicator.config(bg=navColor)
            settings_indicator.config(bg=navColor)
            mainSettings_indicator.config(bg=navColor)
            indicator_lb.config(bg="white")
            for frame in MainFrame.winfo_children():
                frame.destroy()
            currenScreen = page(MainFrame)
            navMenuClose()


class mainSettingsScreenClass:

    def __init__(main, MainFrame):

        def ApplySettings():
            global SaveControler
            SaveControler = SoortControler.get()

        SettingsFrame = tk.Frame(MainFrame, bg="white")
        SettingsFrame.place(relwidth=1.0, relheight=1.0, x=50)

        SoortControlerlabel = tk.Label(
            SettingsFrame, text="Soort Controle:", bg="white", fg="black", font=("Arial", 10))
        SoortControlerlabel.grid(row=0, column=0, sticky="e")
        SoortControler = tk.StringVar()
        soortControlerMenu = tk.OptionMenu(
            SettingsFrame, SoortControler, "Gui", "ModBusTCP", "PLC S7-1500/1200/400/300", "logo!", "PLCSim")
        soortControlerMenu.grid(row=0, column=1, sticky="ew")
        SoortControler.set(SaveControler)

        SaveButton = tk.Button(
            SettingsFrame, text="Apply Settings", bg="white", activebackground="white", command=ApplySettings)
        SaveButton.grid(row=12, column=3, pady=(10, 0))

        ExportButton = tk.Button(
            SettingsFrame, text="Export config", bg="white", activebackground="white", command=main.ExportConfig)
        ExportButton.grid(row=12, column=4, padx=(30, 0), pady=(10, 0))

        LoadButton = tk.Button(
            SettingsFrame, text="Load config", bg="white", activebackground="white", command=main.ImportConfig)
        LoadButton.grid(row=12, column=5, padx=(10, 0), pady=(10, 0))

    def updateData(self, mainConfig: mainConfigClass, processConfig: tankSimConfigurationClass, processStatus: tankSimStatusClass):
        global SaveControler, importCommand, exportCommand

        # define csv fileType for filedialog functions
        csvFileType = [
            ('Comma-separated values', '*.csv'), ('All Files', '*.*'),]

        # overwrite config and status after other changes done by gui
        if (importCommand):
            file = filedialog.askopenfilename(
                filetypes=csvFileType, defaultextension=csvFileType)
            # only try to import when there was a file selected
            if (file):
                mainConfig.loadFromFile(file)
            importCommand = False  # reset import command flag

        # write data to status and config
        if (SaveControler == "Gui"):
            mainConfig.plcGuiControl = "gui"
        else:
            mainConfig.plcGuiControl = "plc"
            mainConfig.plcProtocol = SaveControler

        # export mainConfig after all changes are done
        if (exportCommand):
            file = filedialog.asksaveasfilename(
                filetypes=csvFileType, defaultextension=csvFileType)
            # only try to export when the was a file selected
            if (file):
                # create file, add header, add config variables
                mainConfig.saveToFile(file, True)
            exportCommand = False

    def ExportConfig(self):
        global exportCommand
        exportCommand = True

    def ImportConfig(self):
        global importCommand
        importCommand = True


class mainGui:

    def __init__(self) -> None:
        global currenScreen

        self.root = tk.Tk()
        # when window is closed, stop the rest of the program
        self.root.protocol("WM_DELETE_WINDOW", self.onExit)
        self.Main = MainScherm(self.root)
        self.nav = NavigationFrame(self.root, self.Main.MainFrame)
        self.Tank = tankSimProcessScreenClass(self.Main.MainFrame)
        currenScreen = self.Tank

    def updateGui(self) -> None:
        self.root.update_idletasks()
        self.root.update()

    def updateDataMain(self, mainConfig: mainConfigClass) -> None:
        global exitProgram, TryConnectPending, ip_adress

        mainConfig.doExit = exitProgram

        if (TryConnectPending):
            mainConfig.plcIpAdress = ip_adress
            mainConfig.tryConnect = True  # set flag
            TryConnectPending = False  # clear flag

    # TODO: change process config and status to base class

    def updateData(self, mainConfig: mainConfigClass, processConfig: tankSimConfigurationClass, processStatus: tankSimStatusClass) -> None:
        global currenScreen
        currenScreen.updateData(
            mainConfig, processConfig, processStatus)

    def onExit(self) -> None:
        global exitProgram
        exitProgram = True
