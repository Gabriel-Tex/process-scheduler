"""
Escalonadores por Prioridade Estática — cooperativo e preemptivo.

Dois algoritmos neste módulo (compartilham a mesma base parametrizável):

PrioridadeCooperativa (nome interno: 'prioc')
    Algoritmo: não-preemptivo.
    Chave de seleção: maior prioridade_estatica.
    Herda de EscalonadorPorChave:
        - chave(p) = -p.prioridade_estatica
        - preemptivo = False
    Validação manual (dataset Seção 3):
        tt médio = 6,6 | tw médio = 3,8 | trocas de contexto = 4

PrioridadePreemptiva (nome interno: 'priop')
    Algoritmo: preemptivo.
    Chave de seleção: maior prioridade_estatica, reavaliada a cada tick.
    Herda de EscalonadorPorChave:
        - chave(p) = -p.prioridade_estatica
        - preemptivo = True
    Validação manual (dataset Seção 3):
        tt médio = 5,6 | tw médio = 2,8 | trocas de contexto = 6

Convenção de prioridade:
    Maior valor numérico = maior prioridade.
    Suposição documentada em docs/decisoes_implementacao.md.
"""

from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import registrar
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_prioridade_estatica(processo: Processo) -> int:
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
