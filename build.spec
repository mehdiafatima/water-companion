# -*- mode: python ; coding: utf-8 -*-
"""
build.spec
==========
PyInstaller build specification for Water Companion.

Build:
    pyinstaller build.spec

Output:
    dist/water-companion/   (one-dir bundle)
    dist/water-companion.exe (Windows)
"""

import sys
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH)

a = Analysis(
    [str(project_root / "water_companion" / "cli.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PySide6 modules that PyInstaller may miss
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtNetwork",
        # Our own modules
        "water_companion.main",
        "water_companion.cli",
        "water_companion.core.reminder_manager",
        "water_companion.core.messages",
        "water_companion.mascot.water_drop_widget",
        "water_companion.mascot.animations",
        "water_companion.ui.setup_window",
        "water_companion.ui.reminder_window",
        "water_companion.ui.tray_manager",
        "water_companion.ui.styles",
        "water_companion.settings.config",
        "water_companion.utils.constants",
        "water_companion.utils.logger",
        # Typer / Rich
        "typer",
        "rich",
        "click",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "PIL",
        "cv2",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="water-companion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No console window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",  # Uncomment if you export a .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="water-companion",
)
