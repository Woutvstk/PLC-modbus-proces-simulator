# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# -----------------------------
# 1. Hidden imports
# -----------------------------
hiddenimports = []
hiddenimports += collect_submodules("pymodbus")
hiddenimports += collect_submodules("asyncio")

# -----------------------------
# 2. Data files
# -----------------------------
datas = []

# GUI media (UI, QSS, SVG, PNG, ICO)
datas = [
    ('src/gui/media', 'gui/media'),
    ('src/gui/media/icon', 'gui/media/icon'),
    ('src/gui/media/media', 'gui/media/media'),
]


datas += collect_data_files("src/gui/media")
datas += collect_data_files("src/gui/media/icon")
datas += collect_data_files("src/gui/media/media")

# GUI pages
datas += collect_data_files("src/gui/pages")

# IO configuration files
datas += collect_data_files("src/IO", includes=["*.json", "*.xml"])

# PLCSimS7 protocol files
datas += collect_data_files("src/IO/protocols/PLCSimS7/NetToPLCsim")

# PLCSimAPI DLLs
datas += collect_data_files("src/IO/protocols/PLCSimAPI")

# Simulations
datas += collect_data_files("src/simulations")

# TankSim
datas += collect_data_files("src/tankSim")

# -----------------------------
# 3. External binaries
# -----------------------------
binaries = [
    ("src/IO/protocols/PLCSimS7/NetToPLCsim/NetToPLCsim.exe", "."),
    ("src/IO/protocols/PLCSimS7/NetToPLCsim/IsoToS7online.dll", "."),
    ("src/IO/protocols/PLCSimAPI/SiemensAPI.DLL", "."),
]

# -----------------------------
# 4. Analysis
# -----------------------------
a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# -----------------------------
# 5. Python archive
# -----------------------------
pyz = PYZ(a.pure, a.zipped_data)

# -----------------------------
# 6. EXE (ONEFILE MODE)
# -----------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PLC_Modbus_Proces_Simulator",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

# -----------------------------
# 7. COLLECT
# -----------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="PLC_Modbus_Proces_Simulator",
)
