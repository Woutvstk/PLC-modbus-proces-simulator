import tkinter as tk
import pathlib
import os
from tkinter import *
from PIL import Image, ImageTk


def getAbsolutePath(relativePath: str) -> str:
    current_dir = pathlib.Path(__file__).parent.resolve()
    return os.path.join(current_dir, relativePath)


# Maak een nieuw venster
root = tk.Tk()
root.title("PID Regelaar Tank")
# toolbar
root.frame = Frame(root, height=50, bg="lightgrey")
root.frame.pack(fill=X)

# hamburger menu button
hamburgerImage = Image.open(getAbsolutePath("media\\HamburgerIcon.png")
                            )  # Replace with your image file path
resizedHamburgerImage = hamburgerImage.resize((45, 45))
imgHamburger = ImageTk.PhotoImage(resizedHamburgerImage)
Hamburger = tk.Button(root, border=0, width=50, height=48,
                      background="lightgrey", image=imgHamburger)
Hamburger.place(x=0, y=0)


# connection button
connectionImage = Image.open(getAbsolutePath("media\\connect.png")
                             )  # Replace with your image file path
resizedConnectionImage = connectionImage.resize((35, 20))
imgConection = ImageTk.PhotoImage(resizedConnectionImage)
Connect = tk.Button(root, image=imgConection, command=root.destroy)
Connect.place(x=1400, y=15)

is_maximized = True
# 'zoomed' werkt op Windows om het venster te maximaliseren
root.state('zoomed')


def toggle_fullscreen(event=None):
    """Toggle windowed fullscreen / maximize (gebonden aan F11)."""
    global is_maximized
    if is_maximized:
        root.state('normal')
        is_maximized = False
    else:
        root.state('zoomed')
        is_maximized = True


def exit_fullscreen(event=None):
    """Zet het venster terug naar normaal (gebonden aan Escape)."""
    global is_maximized
    root.state('normal')
    is_maximized = False


# Bind toetsen
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', exit_fullscreen)


root.mainloop()
