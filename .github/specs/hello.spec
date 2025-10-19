# hello.spec
# Force PyInstaller to create a macOS .app bundle for hello.py

block_cipher = None

a = Analysis(
    ['hello.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter'],   # ensure tkinter is included
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hello',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # this makes it a GUI app
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hello',
)

app = BUNDLE(
    coll,
    name='hello.app',
    icon=None,
    bundle_identifier='com.example.hello',
)