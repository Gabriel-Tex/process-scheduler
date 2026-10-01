"""Round-Robin com prioridade dinâmica; envelhecimento por quantum completo.

Ao fechar uma fatia completa, apenas os processos já em espera recebem aging.
Não há envelhecimento na primeira escolha, no ócio ou em fatia incompleta.
Maior número = maior prioridade; a escolha restaura a prioridade estática.
"""
import random
from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from .base import EscalonadorBase, desempatar
from .factory import registrar


class RoundRobinAging(EscalonadorBase):
    nome = "Round-Robin + envelhecimento"

    def __init__(self, configuracao: Configuracao, aleatorio: random.Random):
        if configuracao.quantum <= 0 or configuracao.aging <= 0:
            raise ValueError("quantum e aging devem ser > 0")
        self.quantum = configuracao.quantum
        self.aging = configuracao.aging
        self.aleatorio = aleatorio
        # Lista evita chaves obsoletas de heap após alterar prioridades.
        self.prontos: list[Processo] = []
        self.consumido = 0

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        processo.prioridade_dinamica = processo.prioridade_estatica
        self.prontos.append(processo)

    def selecionar_proximo(self, tempo: int, em_execucao: Processo | None) -> Processo | None:
        if em_execucao is not None and em_execucao.tempo_restante > 0:
            if self.consumido < self.quantum:
                return em_execucao
            self.prontos.append(em_execucao)
        self.consumido = 0
        self.prontos = [p for p in self.prontos if p.tempo_restante > 0]
        if not self.prontos:
            return None
        maior = max(p.prioridade_dinamica for p in self.prontos)
        candidatos = [p for p in self.prontos if p.prioridade_dinamica == maior]
        escolhido = desempatar(candidatos, em_execucao, self.aleatorio)
        self.prontos = [p for p in self.prontos if p is not escolhido]
        escolhido.prioridade_dinamica = escolhido.prioridade_estatica
        return escolhido

    def ao_finalizar_tick(self, tempo: int, em_execucao: Processo | None) -> None:
        if em_execucao is None:
            return
        self.consumido += 1
        if self.consumido == self.quantum:
            for processo in self.prontos:
                if processo.tempo_restante > 0:
                    processo.prioridade_dinamica += self.aging


registrar("rr_prio_aging", RoundRobinAging)
