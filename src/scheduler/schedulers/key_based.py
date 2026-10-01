"""Escalonador base para políticas que escolhem pelo menor valor de chave."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.base import EscalonadorBase, desempatar


class EscalonadorPorChave(EscalonadorBase):
    """Seleciona processos prontos pelo menor valor de uma chave recalculada."""

    def __init__(
        self,
        configuracao: Configuracao,
        chave: Callable[[Processo], int],
        preemptivo: bool,
        aleatorio: random.Random | None = None,
    ) -> None:
        """Inicializa a política, a fila de prontos e a aleatoriedade."""
        self._chave = chave
        self._preemptivo = preemptivo
        self._prontos: list[Processo] = []
        self._aleatorio = aleatorio if aleatorio is not None else random.Random()

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        """Adiciona à lista o processo que acabou de chegar."""
        self._prontos.append(processo)

    def selecionar_proximo(
        self, tempo: int, em_execucao: Processo | None
    ) -> Processo | None:
        """Escolhe o menor valor de chave entre os processos elegíveis."""
        self._prontos = [processo for processo in self._prontos if not processo.finalizado]
        if em_execucao is not None and em_execucao.finalizado:
            em_execucao = None

        if not self._preemptivo and em_execucao is not None:
            return em_execucao

        candidatos = list(self._prontos)
        if self._preemptivo and em_execucao is not None:
            candidatos.append(em_execucao)
        if not candidatos:
            return None

        valores_chave = [
            (processo, self._chave(processo)) for processo in candidatos
        ]
        menor_chave = min(valor for _, valor in valores_chave)
        empatados = [
            processo
            for processo, valor in valores_chave
            if valor == menor_chave
        ]
        escolhido = self._desempatar(empatados, em_execucao)

        self._prontos = [
            processo for processo in self._prontos if processo is not escolhido
        ]
        # O processo interrompido continua pronto para disputar a próxima seleção.
        if (
            self._preemptivo
            and em_execucao is not None
            and em_execucao is not escolhido
            and all(processo is not em_execucao for processo in self._prontos)
        ):
            self._prontos.append(em_execucao)

        return escolhido

    def _desempatar(
        self, candidatos: Sequence[Processo], em_execucao: Processo | None
    ) -> Processo:
        return desempatar(candidatos, em_execucao, self._aleatorio)