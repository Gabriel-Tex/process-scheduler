"""Resultado imutável de uma execução; não depende da interface gráfica."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoSimulacao:
    nome_algoritmo: str
    tt_medio: float
    tw_medio: float
    trocas_contexto: int
    diagrama: str
    # Cada posição é um segundo: ID na CPU e IDs presentes antes de executar.
    registros: tuple[tuple[str | None, frozenset[str]], ...] = ()
    # Pares (ID, espera total em segundos), na ordem original da entrada.
    esperas: tuple[tuple[str, int], ...] = ()
