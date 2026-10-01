"""Escalonador FCFS (First-Come, First-Served)."""

from __future__ import annotations

import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.base import EscalonadorBase, desempatar
from src.scheduler.schedulers.factory import registrar


class FCFS(EscalonadorBase):
    """Escalona processos pela ordem de chegada, sem preempção."""

    def __init__(
        self, configuracao: Configuracao, aleatorio: random.Random | None = None
    ) -> None:
        """Inicializa a fila de prontos e a fonte de aleatoriedade."""
        self._prontos: list[Processo] = []
        self._aleatorio = aleatorio if aleatorio is not None else random.Random()

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        """Adiciona à lista o processo que acabou de chegar."""
        self._prontos.append(processo)

    def selecionar_proximo(
        self, tempo: int, em_execucao: Processo | None
    ) -> Processo | None:
        """Mantém a CPU atual ou escolhe o pronto com chegada mais antiga."""
        if em_execucao is not None and not em_execucao.finalizado:
            return em_execucao

        self._prontos = [processo for processo in self._prontos if not processo.finalizado]
        if not self._prontos:
            return None

        menor_instante = min(processo.instante_criacao for processo in self._prontos)
        candidatos = [
            processo
            for processo in self._prontos
            if processo.instante_criacao == menor_instante
        ]
        return desempatar(candidatos, em_execucao, self._aleatorio)


registrar("fcfs", FCFS)
