# hello.spec
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('tkinter')

app = BUNDLE(
    name='hello.app',
    app=['hello.py'],
    icon=None,
    bundle_identifier='com.example.hello',
)
