import platform
from argparse import ArgumentParser

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.osx import BUNDLE
from tomllib import load

parser = ArgumentParser()
parser.add_argument("--portable", action="store_true")
parser.add_argument("--cppready", action="store_true")
options = parser.parse_args()

if options.portable and options.cppready:
    raise Exception("Both portable and cppready specified.")

with open("pyproject.toml", "rb") as file:
    pyproject = load(file)["project"]

system = platform.system()

name = pyproject["name"] if system == "Windows" else "tagstudio"
icon = None
if system == "Windows":
    icon = "src/tagstudio/resources/icon.ico"
elif system == "Darwin":
    icon = "src/tagstudio/resources/icon.icns"


datafiles = [
    ("src/tagstudio/qt/*.json", "tagstudio/qt"),
    ("src/tagstudio/qt/*.qrc", "tagstudio/qt"),
    ("src/tagstudio/resources", "tagstudio/resources"),
]
if options.cppready:
    datafiles += [("src/tagstudio/main.py", "tagstudio")]

a = Analysis(
    ["src/tagstudio/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datafiles,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    excludes=[],
    runtime_hooks=[],
    noarchive=options.cppready,
    optimize=0,
)

# PyInstaller doesn't inject its bootstrapping scripts if there's not
# at least one archive present in the executable.
# Since we don't have a choice whether or not an exe is generated, we
# might as well have it be functional..
pyz = PYZ(a.pure if not options.cppready else [])

include = [a.scripts]
if options.portable:
    include += (a.binaries, a.datas)
exe = EXE(
    pyz,
    *include,
    [],
    bootloader_ignore_signals=False,
    console=False,
    hide_console="hide-early",
    disable_windowed_traceback=False,
    debug=False,
    name=name,
    exclude_binaries=not options.portable,
    icon=icon,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
)

coll = (
    None
    if options.portable
    else COLLECT(
        exe,
        a.binaries,
        a.datas,
        # 'a.scripts' just ends up being the hooks plus the user specified
        # scripts to analyse.
        # Since we manually get it as data in the tagstudio folder, there
        # is no need for it.
        #a.scripts if options.cppready else [],
        a.pure if options.cppready else [],
        name=name,
        strip=False,
        upx=True,
        upx_exclude=[],
    )
)

if system == "Darwin":
    app = BUNDLE(
        exe if coll is None else coll,
        name=f"{pyproject['name']}.app",
        icon=icon,
        bundle_identifier="com.cyanvoxel.tagstudio",
        version=pyproject["version"],
        info_plist={
            "NSAppleScriptEnabled": False,
            "NSPrincipalClass": "NSApplication",
        },
    )

# vi: ft=python
