"""Escalonador SJF (Shortest Job First)."""

from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import registrar
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_duracao_original(processo: Processo) -> int:
    return processo.tempo_processamento


class SJF(EscalonadorPorChave):
    """Escalona sem preempção pelo menor tempo de processamento original."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Configura a seleção SJF sem preempção."""
        super().__init__(
            configuracao,
            _chave_duracao_original,
            preemptivo=False,
            aleatorio=aleatorio,
        )


registrar("sjf", SJF)
