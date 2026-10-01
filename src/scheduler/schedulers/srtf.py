"""Escalonador SRTF (Shortest Remaining Time First)."""

from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import registrar
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_tempo_restante(processo: Processo) -> int:
    return processo.tempo_restante


class SRTF(EscalonadorPorChave):
    """Escalona preemptivamente pelo menor tempo restante atual."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Configura a seleção SRTF preemptiva."""
        super().__init__(
            configuracao,
            _chave_tempo_restante,
            preemptivo=True,
            aleatorio=aleatorio,
        )


registrar("srtf", SRTF)
