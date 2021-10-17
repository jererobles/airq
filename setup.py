from setuptools import setup

APP = ["airq/__main__.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "icon.icns",
    "plist": {
        "LSUIElement": True,
        "CFBundleShortVersionString": "0.1.0",
    },
    "packages": ["rumps"],
}

setup(
    name="AirQ",
    version="0.2",
    license="MIT",
    long_description=open("README.md").read(),
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
