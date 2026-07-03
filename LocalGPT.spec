# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, copy_metadata

# --------------------------------------------------
# Files that must ship inside the bundle.
#
# app.py and the helper modules are run/imported by
# Streamlit at RUNTIME, so PyInstaller's static analysis
# of launcher.py never sees them. We add them as data
# files so they land next to the frozen app.
# --------------------------------------------------

datas = [
    ('assets', 'assets'),
    ('app.py', '.'),
    ('chatbot.py', '.'),
    ('chat_manager.py', '.'),
    ('config.py', '.'),
    ('ollama_utils.py', '.'),
    ('utils.py', '.'),
    ('file_reader.py', '.'),
]

binaries = []

hiddenimports = ['streamlit', 'webview', 'requests', 'ollama']

# Streamlit and ollama ship data files and read their own
# package metadata at runtime; collect all of it.
for pkg in ['streamlit', 'ollama', 'pypdf', 'docx', 'PIL']:
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

# Several libraries look up their version via importlib.metadata.
for pkg in ['streamlit', 'ollama', 'requests', 'pywebview', 'pypdf', 'python-docx']:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalGPT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # Keep the console visible for your FIRST build so you can
    # read any startup errors. Once it works, set this to False
    # and rebuild for a clean windowed app.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LocalGPT',
)
