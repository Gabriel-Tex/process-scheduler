"""Escalonador FCFS (First-Come, First-Served)."""

from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import registrar
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_instante_criacao(processo: Processo) -> int:
    return processo.instante_criacao


class FCFS(EscalonadorPorChave):
    """Escalona processos pela ordem de chegada, sem preempção."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Configura a seleção FCFS sem preempção."""
        super().__init__(
            configuracao,
            _chave_instante_criacao,
            preemptivo=False,
            aleatorio=aleatorio,
        )


registrar("fcfs", FCFS)
