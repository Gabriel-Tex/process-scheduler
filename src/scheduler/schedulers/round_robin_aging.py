"""Round-Robin com prioridade dinâmica; envelhecimento por fronteira de quantum.

A cada fronteira de quantum (quantum esgotado, término antecipado, ou CPU ociosa com prontos):
1. O processo escolhido tem pd restaurada para pe.
2. Todos os demais prontos recebem pd += aging.
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
        self.prontos: list[Processo] = []
        self.consumido = 0

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        processo.prioridade_dinamica = processo.prioridade_estatica
        self.prontos.append(processo)

    def selecionar_proximo(self, tempo: int, em_execucao: Processo | None) -> Processo | None:
        # Se está rodando e não esgotou quantum nem terminou, continua
        if em_execucao is not None and em_execucao.tempo_restante > 0:
            if self.consumido < self.quantum:
                return em_execucao
            # Se esgotou quantum, volta com pd = pe
            em_execucao.prioridade_dinamica = em_execucao.prioridade_estatica
            self.prontos.append(em_execucao)

        # Chegamos a uma fronteira de quantum (esgotou, terminou antecipado ou era ocioso)
        self.consumido = 0
        
        # Filtrar terminados (caso existam)
        self.prontos = [p for p in self.prontos if p.tempo_restante > 0]
        
        if not self.prontos:
            return None
            
        # Selecionar o maior pd
        maior = max(p.prioridade_dinamica for p in self.prontos)
        candidatos = [p for p in self.prontos if p.prioridade_dinamica == maior]
        escolhido = desempatar(candidatos, em_execucao, self.aleatorio)
        
        self.prontos = [p for p in self.prontos if p is not escolhido]
        
        # O escolhido tem pd restaurada para pe
        escolhido.prioridade_dinamica = escolhido.prioridade_estatica
        
        # Todos os demais prontos recebem pd += aging
        for p in self.prontos:
            p.prioridade_dinamica += self.aging
            
        return escolhido

    def ao_finalizar_tick(self, tempo: int, em_execucao: Processo | None) -> None:
        if em_execucao is not None:
            self.consumido += 1

registrar("rr_prio_aging", RoundRobinAging)
