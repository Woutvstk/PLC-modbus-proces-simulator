
import tkinter as tk
import pathlib
import os
from PIL import Image, ImageTk

navColor = '#383838'
klepstandboven = 20
klepstandonder = 50
hoogte = 2000
volumetank = 2000
HoogteVatGUI = 248  # hoogte van tank
StartHoogteVat = 488


SaveKleur = "Blue"
SaveBreedte = 1000
SaveHoogte = 2000
SaveDebiet = 100
SaveDichtheid = 997
SaveControler = "Logo"
SaveKlepen = 1
SaveWeerstand = 1
SaveHoogtemeting = 1


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
        main.conFrame.place(relwidth=1.0,  x=50, y=4)

        connectButton = tk.Button(main.conFrame, text="Connect",
                                  bg=conColor, activebackground=conColor, fg="white")
        connectButton.place(x=830, y=10)
        AdresLabel = tk.Label(main.conFrame, text="IP Adress:",
                              bg=conColor, fg="White", font=("Arial", 10))
        AdresLabel.place(x=900, y=10)
        Adres = tk.Entry(main.conFrame, bg=conColor,
                         fg="White", font=("Arial", 10))
        Adres.place(x=970, y=12.5)
        Adres.insert(0, "192.168.111.10")

        main.MainFrame = tk.Frame(main.root, bg="white")
        main.MainFrame.place(relwidth=1.0, relheight=1.0, x=50, y=50)


class TankScherm:

    def __init__(main, MainFrame,):

        main.canvas = tk.Canvas(
            MainFrame, width=1000, height=700, bg="white", border=0, highlightthickness=0)
        main.canvas.pack(fill=tk.BOTH, expand=True)

        DebietView = tk.Label(
            main.canvas, text=SaveDebiet, bg="white", font=("Arial", 10))
        DebietView.place(x=70, y=140)
        eenheidDebiet = tk.Label(
            main.canvas, text="(l/min)", bg="white", font=("Arial", 10))
        eenheidDebiet.place(relx=0.085, y=140)
        main.canvas.create_line(
            65, 130, 160, 130, fill="black", arrow="last", width=5)

        main.canvas.create_line(740, 490, 740, StartHoogteVat-hoogte /
                                volumetank*HoogteVatGUI, fill="red", arrow="both", width=5)
        actueleHoogte = tk.Label(
            main.canvas, text=hoogte, fg="red", bd=0, bg="white", font=("Arial", 10))
        actueleHoogte.place(x=750, y=StartHoogteVat-hoogte /
                            volumetank*HoogteVatGUI/2)
        actueleHoogteEenheid = tk.Label(
            main.canvas, text="mm", fg="red", bd=0, bg="white", font=("Arial", 10))
        actueleHoogteEenheid.place(x=780, y=StartHoogteVat-hoogte /
                                   volumetank*HoogteVatGUI/2)

        vatx1, vaty1 = 480, 490
        vatx2, vaty2 = 720, 210
        vatx3, vatx4 = 483, 718

        # horizontale buis bovenaan
        buisx1, buisy1 = 0, 80
        buisx2, buisy2 = 612.5, 80
        buisx3, buisy3 = 0, 105
        buisx4, buisy4 = 587.5, 105

        # verticale buis bovenaan boven klep
        vbuisx1, vbuisy1 = 612.5, 80
        vbuisx2, vbuisy2 = 612.5, 140
        vbuisx3, vbuisy3 = 587.5, 105
        vbuisx4, vbuisy4 = 587.5, 140
        # verticale buis bovenaan onder klep
        vbuisx5, vbuisy5 = 612.5, 200
        vbuisx6, vbuisy6 = 612.5, 230
        vbuisx7, vbuisy7 = 587.5, 200
        vbuisx8, vbuisy8 = 587.5, 230

        # verticale buis onderaan boven klep
        Abuisx1, Abuisy1 = 612.5, 490
        Abuisx2, Abuisy2 = 612.5, 520
        Abuisx3, Abuisy3 = 587.5, 490
        Abuisx4, Abuisy4 = 587.5, 520
        # verticale buis onderaan onder klep
        Abuisx5, Abuisy5 = 612.5, 580
        Abuisx6, Abuisy6 = 612.5, 700
        Abuisx7, Abuisy7 = 587.5, 580
        Abuisx8, Abuisy8 = 587.5, 700

        # Tekenen van de tank
        main.canvas.create_rectangle(
            vatx1, vaty1, vatx2, vaty2, outline="black", width=5)
        main.canvas.create_line(vatx3, vaty2, vatx4,
                                vaty2, fill="white", width=5)

        # tekenen van de verticale buis bovenaan onder klep
        main.canvas.create_line(vbuisx5, vbuisy5, vbuisx6,
                                vbuisy6, fill="black", width=5)
        main.canvas.create_line(vbuisx7, vbuisy7, vbuisx8,
                                vbuisy8, fill="black", width=5)

        # tekenen van de verticale buis onderaan boven klep
        main.canvas.create_line(Abuisx1, Abuisy1, Abuisx2,
                                Abuisy2, fill="black", width=5)
        main.canvas.create_line(Abuisx3, Abuisy3, Abuisx4,
                                Abuisy4, fill="black", width=5)
        # tekenen van de verticale buis onderaan onder klep
        main.canvas.create_line(Abuisx5, Abuisy5, Abuisx6,
                                Abuisy6, fill="black", width=5)
        main.canvas.create_line(Abuisx7, Abuisy7, Abuisx8,
                                Abuisy8, fill="black", width=5)

        # water in buis
        main.canvas.create_rectangle(
            buisx1, buisy1, buisx2, buisy4, outline="black", width=5, fill="blue")
        main.canvas.create_rectangle(
            vbuisx1, vbuisy1, vbuisx4, vbuisy4, outline="black", width=5, fill="blue")
        main.canvas.create_line(buisx4, buisy1+3, buisx4,
                                buisy3-2, fill="blue", width=5)
        if klepstandboven > 0 and klepstandonder <= 0 and hoogte > 0:
            print("Klep is open")
            # klep vol water
            main.canvas.create_polygon(
                580, 140, 620, 140, 600, 170, outline="black", width=5, fill="Blue")
            main.canvas.create_polygon(
                580, 200, 620, 200, 600, 170, outline="black", width=5, fill="Blue")

            # tekenen van de klep onderaan
            main.canvas.create_polygon(
                580, 520, 620, 520, 600, 550, outline="black", width=5, fill="White")
            main.canvas.create_polygon(
                580, 580, 620, 580, 600, 550, outline="black", width=5, fill="White")

            # water in buis
            main.canvas.create_rectangle(600.9+klepstandboven*0.105, vbuisy5+3,
                                         600.9-klepstandboven*0.105, vaty1-2, width=0, fill="Blue")

            main.canvas.create_rectangle(Abuisx1, Abuisy1,
                                         Abuisx4, Abuisy4, outline="black", width=5, fill="Blue")
            # water in tank
            main.canvas.create_rectangle(
                vatx1+3, vaty1-2, vatx2-2, StartHoogteVat-hoogte/volumetank*HoogteVatGUI, width=0, fill="Blue")

        elif klepstandboven <= 0 and klepstandonder > 0 and hoogte > 0:
            print("Klep boven toe klep onder open")
            # klep
            main.canvas.create_polygon(
                580, 140, 620, 140, 600, 170, outline="black", width=5, fill="white")
            main.canvas.create_polygon(
                580, 200, 620, 200, 600, 170, outline="black", width=5, fill="white")

            # tekenen van de klep onderaan
            main.canvas.create_polygon(
                580, 520, 620, 520, 600, 550, outline="black", width=5, fill="Blue")
            main.canvas.create_polygon(
                580, 580, 620, 580, 600, 550, outline="black", width=5, fill="Blue")

            # water in buis

            main.canvas.create_rectangle(Abuisx1, Abuisy1,
                                         Abuisx4, Abuisy4, outline="black", width=5, fill="Blue")
            # water in tank
            main.canvas.create_rectangle(
                vatx1+3, vaty1-2, vatx2-2,  StartHoogteVat-(hoogte/volumetank*HoogteVatGUI), width=0, fill="Blue")
            # water in buis onderste klep

            main.canvas.create_rectangle(600.9+klepstandonder*0.105, Abuisy5+3,
                                         600.9-klepstandonder*0.105, Abuisy6, width=0, fill="Blue")
        elif klepstandboven > 0 and klepstandonder > 0 and hoogte > 0:
            print("bijde kleppen open")

            # klep
            main.canvas.create_polygon(
                580, 140, 620, 140, 600, 170, outline="black", width=5, fill="Blue")
            main.canvas.create_polygon(
                580, 200, 620, 200, 600, 170, outline="black", width=5, fill="Blue")

            # tekenen van de klep onderaan
            main.canvas.create_polygon(
                580, 520, 620, 520, 600, 550, outline="black", width=5, fill="Blue")
            main.canvas.create_polygon(
                580, 580, 620, 580, 600, 550, outline="black", width=5, fill="Blue")

            # water in buis bovenste klep
            main.canvas.create_rectangle(600.9+klepstandboven*0.105, vbuisy5+3,
                                         600.9-klepstandboven*0.105, vaty1-2, width=0, fill="Blue")

            main.canvas.create_rectangle(Abuisx1, Abuisy1,
                                         Abuisx4, Abuisy4, outline="black", width=5, fill="Blue")
            # water in tank
            main.canvas.create_rectangle(
                vatx1+3, vaty1-2, vatx2-2, StartHoogteVat-(hoogte/volumetank*HoogteVatGUI), width=0, fill="Blue")
            # water in buis onderste klep
            main.canvas.create_rectangle(600.9+klepstandonder*0.105, Abuisy5+3,
                                         600.9-klepstandonder*0.105, Abuisy6, width=0, fill="Blue")
        elif klepstandboven <= 0 and klepstandonder > 0 and hoogte <= 0:
            print("Klep onder open hoogte 0")
            # klep
            main.canvas.create_polygon(
                580, 140, 620, 140, 600, 170, outline="black", width=5, fill="white")
            main.canvas.create_polygon(
                580, 200, 620, 200, 600, 170, outline="black", width=5, fill="white")

            # tekenen van de klep onderaan
            main.canvas.create_polygon(
                580, 520, 620, 520, 600, 550, outline="black", width=5, fill="white")
            main.canvas.create_polygon(
                580, 580, 620, 580, 600, 550, outline="black", width=5, fill="white")

        else:
            print("Klep is closed")
            main.canvas.create_polygon(
                580, 140, 620, 140, 600, 170, outline="black", width=5, fill="White")
            main.canvas.create_polygon(
                580, 200, 620, 200, 600, 170, outline="black", width=5, fill="White")

            # tekenen van de klep onderaan
            main.canvas.create_polygon(
                580, 520, 620, 520, 600, 550, outline="black", width=5, fill="White")
            main.canvas.create_polygon(
                580, 580, 620, 580, 600, 550, outline="black", width=5, fill="White")


class SettingsScherm:

    def __init__(main, MainFrame):

        def SaveSettings():
            SaveBreedte = Breedte.get()
            SaveKleur = KleurVloeistof.get()
            SaveDichtheid = Dichtheid.get()
            SaveHoogtemeting = DigitaleHoogte.get()
            SaveWeerstand = RegelbareWeerstand.get()
            SaveKlepen = RegelbareKlepen.get()
            SaveDebiet = Debiet.get()
            SaveHoogte = Hoogte.get()
            SaveControler = SoortControler.get()

        SettingsFrame = tk.Frame(MainFrame, bg="white")
        SettingsFrame.place(relwidth=1.0, relheight=1.0, x=50)
        # dropdown menu voor te kunnen kiezen welke controler je wilt verbinden
        SoortControlerlabel = tk.Label(
            SettingsFrame, text="Soort Controle:", bg="white", fg="black", font=("Arial", 10))
        SoortControlerlabel.grid(row=0, column=0, sticky="e")
        SoortControler = tk.StringVar()
        soortControlerMenu = tk.OptionMenu(
            SettingsFrame, SoortControler, "Logo", "S7 - 1200 PLC", "PLC Simulator")
        soortControlerMenu.grid(row=0, column=1, sticky="ew", )
        SoortControler.set(SaveControler)

        # tekst voor afmetingen vat
        DimensionLabel = tk.Label(
            SettingsFrame, text="Afmetingen Vat:", bg="white", fg="black", font=("Arial", 10))
        DimensionLabel.grid(row=1, column=0, sticky="e", pady=(10, 2))

        # tekst + invoervak voor breedte vat
        BreedteLabel = tk.Label(
            SettingsFrame, text="Breete (mm):", bg="white", fg="black", font=("Arial", 10))
        BreedteLabel.grid(row=2, column=0, sticky="e")
        Breedte = tk.Entry(SettingsFrame)
        Breedte.grid(row=2, column=1)
        Breedte.insert(0, SaveBreedte)

        # tekst + invoervak voor hoogte vat
        HoogteLabel = tk.Label(
            SettingsFrame, text="Hoogte (mm):", bg="white", fg="black", font=("Arial", 10))
        HoogteLabel.grid(row=3, column=0, sticky="e")
        Hoogte = tk.Entry(SettingsFrame)
        Hoogte.grid(row=3, column=1)
        Hoogte.insert(0, SaveHoogte)

        # tekst + invoervak voor toekomend debiet
        DebietLabel = tk.Label(
            SettingsFrame, text="Toekomend debiet (l/min):", bg="white", fg="black", font=("Arial", 10))
        DebietLabel.grid(row=4, column=0, sticky="e")
        Debiet = tk.Entry(SettingsFrame)
        Debiet.grid(row=4, column=1)
        Debiet.insert(0, SaveDebiet)

        # tekst voor welke regeling
        RegelingLabel = tk.Label(
            SettingsFrame, text="Regeling:", bg="white", fg="black", font=("Arial", 10))
        RegelingLabel.grid(row=5, column=0, sticky="e", pady=(10, 2))

        # tekst + checkbox voor regelbare klepen
        RegelbareKlepenLabel = tk.Label(
            SettingsFrame, text="Regelbare klepen:", bg="white", fg="black", font=("Arial", 10))
        RegelbareKlepenLabel.grid(row=6, column=0, sticky="e")
        RegelbareKlepen = tk.BooleanVar()
        RegelbareKlepenCheck = tk.Checkbutton(SettingsFrame,
                                              variable=RegelbareKlepen, onvalue=1, offvalue=0, command=RegelbareKlepenTekenen, bg="white")
        RegelbareKlepenCheck.grid(row=6, column=1, sticky="w")
        RegelbareKlepen.set(SaveKlepen)

        # tekst + checkbox voor regelbare weerstand
        RegelbareWeerstandLabel = tk.Label(
            SettingsFrame, text="Regelbare weerstand:", bg="white", fg="black", font=("Arial", 10))
        RegelbareWeerstandLabel.grid(row=7, column=0, sticky="e")
        RegelbareWeerstand = tk.BooleanVar()
        RegelbareWeerstandCheck = tk.Checkbutton(SettingsFrame,
                                                 variable=RegelbareWeerstand, onvalue=1, offvalue=0, command=RegelbareWeerstandTekenen, bg="white")
        RegelbareWeerstandCheck.grid(row=7, column=1, sticky="w")
        RegelbareWeerstand.set(SaveWeerstand)

        # tekst + checkbox voor Analoge Hoogte meting
        DigitaleHoogteLabel = tk.Label(
            SettingsFrame, text="Digitale hoogte meting:", bg="white", fg="black", font=("Arial", 10))
        DigitaleHoogteLabel.grid(row=8, column=0, sticky="e")
        DigitaleHoogte = tk.BooleanVar()
        DigitaleHoogteCheck = tk.Checkbutton(SettingsFrame,
                                             variable=DigitaleHoogte, onvalue=1, offvalue=0, command=AnalogeHoogteTekenen, bg="white")
        DigitaleHoogteCheck.grid(row=8, column=1, sticky="w")
        DigitaleHoogte.set(SaveHoogtemeting)

        # tekst voor soort vloeistof
        SoortVloeistofLabel = tk.Label(
            SettingsFrame, text="Welke Vloeistof zit er in de tank:", bg="white", fg="black", font=("Arial", 10))
        SoortVloeistofLabel.grid(row=9, column=0, sticky="e", pady=(10, 2))

        # tekst + invoervak voor dichtheid vloeistof
        DichtheidLabel = tk.Label(
            SettingsFrame, text="Dichtheid (kg/m³):", bg="white", fg="black", font=("Arial", 10))
        DichtheidLabel.grid(row=10, column=0, sticky="e")
        Dichtheid = tk.Entry(SettingsFrame)
        Dichtheid.grid(row=10, column=1)
        Dichtheid.insert(0, SaveDichtheid)

        # tekst + dropdown menu voor kleur van vloeistof
        KleurVloeistofLabel = tk.Label(
            SettingsFrame, text="Kleur:", bg="white", fg="black", font=("Arial", 10))
        KleurVloeistofLabel.grid(row=11, column=0, sticky="e")
        KleurVloeistof = tk.StringVar()

        KleurVloeistofMenu = tk.OptionMenu(
            SettingsFrame, KleurVloeistof, *kleuren)
        KleurVloeistofMenu.grid(row=11, column=1, sticky="ew", )
        KleurVloeistof.set(SaveKleur)

        SaveButton = tk.Button(
            SettingsFrame, text="Save Settings", bg="white", activebackground="white", command=SaveSettings)
        SaveButton.grid(row=12, column=2, pady=(10, 0))


def RegelbareKlepenTekenen():
    print("regelbare klepen")


def RegelbareWeerstandTekenen():
    print("regelbare Weerstand")


def AnalogeHoogteTekenen():
    print(" Analoge hoogte meting")


class NavigationFrame:
    def __init__(nav, root, MainFrame):
        navColor = '#383838'
        nav = tk.Frame(root, bg=navColor)
        # icons
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
            HomeText.bind(
                "<Button-1>", lambda e: welkePagina(home_indicator, TankScherm, MainFrame))
            SettingsText = tk.Label(
                nav, text="Settings", bg=navColor, fg="white")
            SettingsText.place(x=45, y=200)
            SettingsText.bind(
                "<Button-1>", lambda e: welkePagina(settings_indicator, SettingsScherm, MainFrame))

        def navMenuClose():
            navMenuAnimatieClose()
            toggleNav.config(text="nav", command=navMenuOpen)

        toggleNav = tk.Button(nav, text="Nav", bg=navColor,
                              bd=0, activebackground=navColor, command=navMenuOpen)
        toggleNav.place(x=4, y=10, width=40, height=40)

        home = tk.Button(nav, text="Home", bg=navColor,
                         bd=0, activebackground=navColor, command=lambda: welkePagina(home_indicator, TankScherm, MainFrame))
        home.place(x=4, y=130, width=40, height=40)
        home_indicator = tk.Label(nav, bg=navColor)
        home_indicator.place(x=3, y=130, width=3, height=40)

        settings = tk.Button(nav, text="Settings",
                             bg=navColor, bd=0, activebackground=navColor, command=lambda: welkePagina(settings_indicator, SettingsScherm, MainFrame))
        settings.place(x=4, y=190, width=40, height=40)
        settings_indicator = tk.Label(nav, bg=navColor)
        settings_indicator.place(x=3, y=190, width=3, height=40)

        def welkePagina(indicator_lb, page, MainFrame):
            home_indicator.config(bg=navColor)
            settings_indicator.config(bg=navColor)
            indicator_lb.config(bg="white")
            for frame in MainFrame.winfo_children():
                frame.destroy()
            page(MainFrame)
            navMenuClose()


kleuren = [
    "Blue",
    "Yellow",
    "Gold",
    "Green",
    "Cyan",
    "Orange",
    "Red",
    "Purple",
    "Pink"

]


root = tk.Tk()
Main = MainScherm(root)
nav = NavigationFrame(root, Main.MainFrame)
Tank = TankScherm(Main.MainFrame)
root.mainloop()
# Maken van navigatie scherm
