import tkinter as tk
import pathlib, os

def  getAbsolutePath (relativePath: str) -> str:
    current_dir = pathlib.Path(__file__).parent.resolve()
    return os.path.join(current_dir, relativePath)





# Maak een nieuw venster
root = tk.Tk()
root.title("PID Regelaar Tank")
connectImage = tk.PhotoImage(file=getAbsolutePath("media\\connect.png"))
Connect= tk.Button(root,image=connectImage, width=800,height= 500, command=root.destroy ).pack()




is_maximized = True
root.state('zoomed')  # 'zoomed' werkt op Windows om het venster te maximaliseren

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
