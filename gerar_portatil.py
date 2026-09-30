"""Gera um .pyz portátil com a biblioteca padrão: python gerar_portatil.py."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def gerar(destino: Path):
    projeto = Path(__file__).resolve().parent
    destino.parent.mkdir(parents=True, exist_ok=True)
    # Diretórios explícitos permitem importar o namespace src de dentro do ZIP.
    with ZipFile(destino, "w", compression=ZIP_DEFLATED) as pacote:
        pacote.writestr("__main__.py", "from iniciar_interface import main\nraise SystemExit(main())\n")
        pacote.write(projeto / "iniciar_interface.py", "iniciar_interface.py")
        pacote.write(projeto / "src", "src/")
        for arquivo in sorted((projeto / "src").rglob("*")):
            if "__pycache__" in arquivo.parts:
                continue
            if arquivo.is_dir() or arquivo.suffix == ".py":
                pacote.write(arquivo, arquivo.relative_to(projeto).as_posix())
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "dist/SimuladorEscalonamento.pyz")
    print(gerar(parser.parse_args().output))
