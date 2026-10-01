"""
Cálculo de métricas e encapsulamento de resultados da simulação.

Este módulo recebe os dados puros de uma simulação (processos finalizados
e histórico de ocupação da CPU) e os transforma nas métricas exigidas pelo
PDF da atividade:
  - tempo médio de execução (turnaround time, tt)
  - tempo médio de espera (waiting time, tw)
  - número de trocas de contexto

As métricas são agrupadas no objeto `ResultadoSimulacao`, juntamente com o
diagrama de tempo correspondente.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src.scheduler.domain.process import Processo
from src.scheduler.simulator.diagram import DiagramaTempo


@dataclass(frozen=True)
class ResultadoSimulacao:
    """Resultado consolidado de um algoritmo após execução pelo motor.

    Campos:
        nome_algoritmo: Identificador do algoritmo executado (ex.: "FCFS").
        tempo_medio_execucao: Média aritmética dos tempos de turnaround (tt)
            de todos os processos simulados. Turnaround = término - criação.
        tempo_medio_espera: Média aritmética dos tempos de espera (tw) de
            todos os processos. Espera = turnaround - duração.
        trocas_contexto: Total de vezes em que a CPU passou a executar um
            processo diferente do que estava executando no tick anterior
            (transições do estado ocioso não contam).
        diagrama: O Gantt vertical acumulado durante a simulação.
    """
    nome_algoritmo: str
    tempo_medio_execucao: float
    tempo_medio_espera: float
    trocas_contexto: int
    diagrama: DiagramaTempo


def calcular_tempos_medios(processos: Sequence[Processo]) -> tuple[float, float]:
    """Calcula o tempo médio de execução e o tempo médio de espera.

    Fórmulas (baseadas nos slides da disciplina):
        - Turnaround (tt) = instante_termino - instante_criacao
        - Espera (tw) = turnaround - duração (tempo_processamento)
        - Média = soma / quantidade

    Args:
        processos: Lista de processos gerados por uma simulação.

    Returns:
        Um tuplo (tempo_medio_execucao, tempo_medio_espera).

    Raises:
        ValueError: Se a lista for vazia (média indefinida) ou se houver
            algum processo não finalizado (métricas seriam inválidas).
    """
    if not processos:
        raise ValueError("Não é possível calcular tempos médios para uma lista vazia de processos.")

    soma_tt = 0
    soma_tw = 0

    for p in processos:
        if not p.finalizado:
            raise ValueError(f"Processo {p.id} não finalizou. Não é possível calcular as métricas.")

        # O cast para int silencia os type checkers, pois finalizado garante
        # que instante_termino não é None.
        termino = int(p.instante_termino)  # type: ignore[arg-type]
        
        # Turnaround time = momento em que saiu do sistema - momento em que chegou
        tt = termino - p.instante_criacao
        
        # Waiting time = tempo total no sistema - tempo efetivamente na CPU
        tw = tt - p.tempo_processamento

        soma_tt += tt
        soma_tw += tw

    n = len(processos)
    return (soma_tt / n, soma_tw / n)


def contar_trocas_contexto(execucoes: Sequence[str | None]) -> int:
    """Conta as trocas de contexto a partir do histórico de uso da CPU.

    Uma troca de contexto ocorre apenas quando a CPU passa a executar um
    processo diferente do tick imediatamente anterior (i.e. transição direta
    entre dois processos distintos). Sair do estado ocioso para executar,
    ou sair da execução para o ócio, não conta como troca.
    Isto está alinhado com o Quadro Comparativo dos slides da disciplina
    (ex.: FCFS com 5 processos enfileirados tem 4 trocas, não 5).

    Args:
        execucoes: Sequência de ids (str) ou None representando quem
            ocupou a CPU no tick 0, tick 1, tick 2, etc.

    Returns:
        O número total de trocas de contexto.
    """
    if not execucoes:
        return 0

    trocas = 0
    for i in range(1, len(execucoes)):
        atual = execucoes[i]
        anterior = execucoes[i - 1]
        
        if atual is not None and anterior is not None and atual != anterior:
            trocas += 1

    return trocas


def construir_resultado(
    nome_algoritmo: str,
    processos: Sequence[Processo],
    execucoes: Sequence[str | None],
    diagrama: DiagramaTempo,
) -> ResultadoSimulacao:
    """Função de conveniência que consolida todas as saídas do motor.

    Aplica as funções de cálculo de métricas e empacota o resultado.

    Args:
        nome_algoritmo: Nome legível do escalonador.
        processos: Lista de processos processados (devem estar finalizados).
        execucoes: O histórico de quem rodou a cada tick (lista de ids).
        diagrama: O diagrama gerado paralelamente.

    Returns:
        O objeto de resultado consolidado pronto para impressão/exibição.
    """
    tt_medio, tw_medio = calcular_tempos_medios(processos)
    trocas = contar_trocas_contexto(execucoes)

    return ResultadoSimulacao(
        nome_algoritmo=nome_algoritmo,
        tempo_medio_execucao=tt_medio,
        tempo_medio_espera=tw_medio,
        trocas_contexto=trocas,
        diagrama=diagrama,
    )
