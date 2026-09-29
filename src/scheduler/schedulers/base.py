"""
Interface abstrata de todos os escalonadores + função de desempate centralizada.

Este módulo define o contrato que cada algoritmo concreto deve implementar
(EscalonadorBase) e a regra única de desempate compartilhada por todos
(desempatar). Nenhum algoritmo concreto é implementado aqui.
"""

from __future__ import annotations
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from src.scheduler.domain.process import Processo


# Interface abstrata
class EscalonadorBase(ABC):
    """
    Contrato comum a todos os algoritmos de escalonamento.

    O motor de simulação interage com qualquer algoritmo exclusivamente
    por estes três métodos (nunca conhece a classe concreta).
    """

    def ao_chegar(self, processo: Processo, tempo: int) -> None:
        """
        Chamado pelo motor quando um processo entra na fila de prontos.

        Implementação padrão: no-op. Sobrescrever quando o algoritmo
        precisar reagir à chegada (ex.: enfileirar o processo).
        """

    @abstractmethod
    def selecionar_proximo(
        self, tempo: int, em_execucao: Processo | None
    ) -> Processo | None:
        """
        Decide quem deve ocupar a CPU neste tick.

        Recebe o processo que estava em execução no tick anterior (ou
        None, se a CPU estava ociosa) e deve devolver o processo que
        deve executar agora (pode ser o mesmo, um diferente, ou None
        se não houver ninguém pronto).
        """

    def ao_finalizar_tick(
        self, tempo: int, em_execucao: Processo | None
    ) -> None:
        """
        Hook opcional, chamado pelo motor ao final de cada tick.

        Implementação padrão: no-op. Usado por algoritmos que precisam
        de contabilidade extra por tick (quantum, envelhecimento).
        """


# Regra de desempate centralizada
def desempatar(
    candidatos: Sequence[Processo],
    em_execucao: Processo | None,
    aleatorio: random.Random,
) -> Processo:
    """
    Aplica a regra de desempate sobre candidatos empatados.

    Pressupostos:
        - ``candidatos`` é não vazio (quem chama já filtrou pelo critério
          principal do algoritmo, ex.: mesma prioridade).
        - Nenhum ``Processo`` é modificado: a função é pura (só observa).

    Critérios aplicados em ordem até restar um único candidato:
        1. Preferir o processo que JÁ ESTÁ na CPU (evita troca desnecessária).
        2. Preferir o processo com MENOR tempo_restante.
        3. Escolha ALEATÓRIA (via ``aleatorio``, nunca random global).
    """
    if len(candidatos) == 1:
        return candidatos[0]

    # Critério 1: processo já em execução
    if em_execucao is not None:
        for c in candidatos:
            if c is em_execucao:
                return c

    # Critério 2: menor tempo_restante
    menor_tempo = min(c.tempo_restante for c in candidatos)
    filtrados = [c for c in candidatos if c.tempo_restante == menor_tempo]

    if len(filtrados) == 1:
        return filtrados[0]

    # Critério 3: aleatório (determinístico se a seed for fixada)
    return aleatorio.choice(filtrados)
