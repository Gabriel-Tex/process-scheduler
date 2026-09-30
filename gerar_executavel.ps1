# Execute na raiz do projeto: powershell -File .\gerar_executavel.ps1
# Requer Python 3.10+ com Tkinter. O usuário do EXE não precisa instalar Python.
param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python -m venv .venv-build
    if ($LASTEXITCODE -ne 0) { throw "Não foi possível criar o ambiente de compilação." }
    $buildPython = Join-Path $PSScriptRoot ".venv-build/Scripts/python.exe"
    & $buildPython -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o empacotador." }
    & $buildPython -m PyInstaller --noconfirm SimuladorEscalonamento.spec
    if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar o executável." }
    Write-Host "Pronto: $PSScriptRoot\dist\SimuladorEscalonamento\SimuladorEscalonamento.exe"
} finally {
    Pop-Location
}
