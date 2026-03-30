# -*- mode: python ; coding: utf-8 -*-
"""
MeowParser PyInstaller 配置文件
支持 Windows 和 Linux 打包
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集数据文件
datas = [
    ('.meowparser/rules', '.meowparser/rules'),  # 规则配置文件
]

# 收集隐藏导入
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'pyqtdarktheme',
    'keyboard',
    'PIL',
    'psutil',
    'pyperclip',
]

# 平台特定的隐藏导入
if sys.platform == 'win32':
    hiddenimports.extend([
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
    ])
elif sys.platform.startswith('linux'):
    hiddenimports.extend([
        'Xlib',
        'Xlib.display',
        'Xlib.X',
    ])

a = Analysis(
    ['meow_parser.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'PyQt5',  # 排除 PyQt5，只使用 PyQt6
        'PySide2',
        'PySide6',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MeowParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)

# Linux 特定配置
if sys.platform.startswith('linux'):
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='MeowParser',
    )
