"""Contrato de apresentação. Não depende de Tkinter nem de algoritmos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TickGUI:
    executando: str | None
    presentes: frozenset[str]


@dataclass(frozen=True)
class ResultadoGUI:
    nome_algoritmo: str
    tt_medio: float
    tw_medio: float
    trocas_contexto: int
    diagrama: str
    ids_processos: tuple[str, ...]
    # None significa que o motor ainda não fornece registros estruturados.
    registros: tuple[TickGUI, ...] | None = None
