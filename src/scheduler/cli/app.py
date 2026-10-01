"""CLI orquestradora para o Simulador de Escalonamento de Processos.

Responsável por fazer o parse dos argumentos, ler os processos e configuração,
executar os algoritmos e repassar os resultados para formatação e saída.
Não implementa lógica de simulação nem formatação de texto.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.io.config_reader import ler_configuracao, ConfiguracaoInvalidaError
from src.scheduler.io.input_reader import ler_processos, EntradaInvalidaError
from src.scheduler.io.output_writer import escrever_resultados
from src.scheduler.schedulers.factory import criar, listar_algoritmos
from src.scheduler.simulator.engine import simular
from src.scheduler.simulator.result import ResultadoSimulacao

def construir_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        prog="python -m scheduler",
        description="Simulador de Escalonamento de Processos.",
        epilog="Exemplo: python -m scheduler --config config.txt --algoritmo rr < entrada.txt"
    )
    parser.add_argument("--config", metavar="CAMINHO", type=str,
                        help="Arquivo de configuração.")
    parser.add_argument("--algoritmo", metavar="NOME", type=str,
                        choices=listar_algoritmos(),
                        help="Roda só esse algoritmo. Sem a flag, roda todos.")
    parser.add_argument("--semente", metavar="N", type=int,
                        help="Inteiro para tornar reprodutível o desempate aleatório.")
    return parser

def resolver_caminho_config(informado: str | None) -> Path | None:
    """Resolve o caminho do arquivo de configuração."""
    if informado is not None:
        p = Path(informado)
        if not p.is_file():
            raise FileNotFoundError(f"Erro na configuração: arquivo não encontrado: {informado}")
        return p

    for padrao in ("config.txt", "config/config.txt"):
        p = Path(padrao)
        if p.is_file():
            return p

    return None

def carregar_configuracao(caminho: Path | None) -> Configuracao:
    """Lê a configuração do arquivo ou devolve uma vazia."""
    if caminho is None:
        return Configuracao()
    with open(caminho, "r", encoding="utf-8") as f:
        return ler_configuracao(f)

def executar_algoritmo(
    nome: str,
    processos: Sequence[Processo],
    configuracao: Configuracao,
    semente: int | None
) -> ResultadoSimulacao:
    """Cria o escalonador e executa a simulação para um algoritmo específico."""
    rng = random.Random(semente)
    escalonador = criar(nome, configuracao, rng)
    return simular(processos, escalonador, nome)

def executar(argv: Sequence[str], entrada: TextIO, saida: TextIO, erro: TextIO) -> int:
    """Orquestra a execução da CLI."""
    parser = construir_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code  # 2 if argparse error, 0 if help

    if entrada.isatty():
        erro.write("Lendo processos da entrada padrão (finalize com Ctrl+D)...\n")
        erro.flush()

    try:
        processos = ler_processos(entrada)
    except (EntradaInvalidaError, ValueError) as e:
        erro.write(f"Erro na entrada: {e}\n")
        return 1

    if not processos:
        erro.write("Erro na entrada: nenhum processo informado.\n")
        return 1

    try:
        caminho_config = resolver_caminho_config(args.config)
    except FileNotFoundError as e:
        erro.write(f"{e}\n")
        return 1

    try:
        configuracao = carregar_configuracao(caminho_config)
    except ConfiguracaoInvalidaError as e:
        erro.write(f"Erro na configuração: {e}\n")
        return 1

    nomes_algoritmos = [args.algoritmo] if args.algoritmo else listar_algoritmos()
    
    resultados: list[ResultadoSimulacao] = []
    codigo_saida = 0

    for nome in nomes_algoritmos:
        try:
            res = executar_algoritmo(nome, processos, configuracao, args.semente)
            resultados.append(res)
        except (ValueError, RuntimeError) as e:
            erro.write(f"Algoritmo '{nome}' não executado: {e}\n")
            codigo_saida = 1

    if resultados:
        escrever_resultados(resultados, saida)

    return codigo_saida

def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada que liga sys.stdin, stdout e stderr à lógica de execução."""
    if argv is None:
        argv = sys.argv[1:]
    return executar(argv, sys.stdin, sys.stdout, sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
