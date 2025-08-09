from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'strip': False,  # This disables binary stripping
    'argv_emulation': False,
    'packages': ["PIL", "uvicorn", "pystray", "tkinter", "pynput"],
    'iconfile': 'JoyCon2Mouse.icns',  # Optional
    'plist': 'Info.plist',
    'excludes': ['rubicon'],
    'resources': ['assets']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
