from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import registrar
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_prioridade_estatica(processo: Processo) -> int:
    # A chave é minimizada, então prioridades maiores usam valor negativo.
    return -processo.prioridade_estatica


class PrioridadeCooperativa(EscalonadorPorChave):
    """Escalona sem preempção; valores maiores representam maior prioridade."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Configura a seleção por prioridade estática sem preempção."""
        super().__init__(
            configuracao,
            _chave_prioridade_estatica,
            preemptivo=False,
            aleatorio=aleatorio,
        )


registrar("prioc", PrioridadeCooperativa)


class PrioridadePreemptiva(EscalonadorPorChave):
    """Escalona preemptivamente; valores maiores representam maior prioridade."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Configura a seleção por prioridade estática com preempção."""
        super().__init__(
            configuracao,
            _chave_prioridade_estatica,
            preemptivo=True,
            aleatorio=aleatorio,
        )


registrar("priop", PrioridadePreemptiva)
