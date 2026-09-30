"""Round-Robin com fila FIFO e preempção somente ao esgotar o quantum."""
from collections import deque
import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from .base import EscalonadorBase
from .factory import registrar


class RoundRobin(EscalonadorBase):
    def __init__(self, configuracao: Configuracao, aleatorio: random.Random):
        if configuracao.quantum <= 0:
            raise ValueError("quantum deve ser > 0")
        self.quantum = configuracao.quantum
        self.fila: deque[Processo] = deque()
        self.consumido = 0

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        self.fila.append(processo)

    def selecionar_proximo(self, tempo: int, em_execucao: Processo | None) -> Processo | None:
        if em_execucao is not None and em_execucao.tempo_restante > 0:
            if self.consumido < self.quantum:
                return em_execucao
            # Chegadas deste instante já foram enfileiradas pelo motor.
            self.fila.append(em_execucao)
        self.consumido = 0
        while self.fila:
            proximo = self.fila.popleft()
            if proximo.tempo_restante > 0:
                return proximo
        return None

    def ao_finalizar_tick(self, tempo: int, em_execucao: Processo | None) -> None:
        if em_execucao is not None:
            self.consumido += 1


registrar("rr", RoundRobin)
