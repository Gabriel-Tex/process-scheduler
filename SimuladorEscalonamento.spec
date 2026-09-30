# Gerado para Windows; executar PyInstaller a partir da raiz do projeto.
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

projeto = Path(SPECPATH)
a = Analysis(
    [str(projeto / "iniciar_interface.py")],
    pathex=[str(projeto)],
    binaries=[],
    datas=[],
    # A fábrica e o serviço usam importlib; incluir esses módulos explicitamente.
    hiddenimports=collect_submodules("src.scheduler"),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="SimuladorEscalonamento",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="SimuladorEscalonamento")
