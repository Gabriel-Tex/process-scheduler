from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src.scheduler.domain.process import Processo
from src.scheduler.simulator.diagram import DiagramaTempo

@dataclass(frozen=True)
class ResultadoSimulacao:
    """Resultado consolidado de um algoritmo após execução pelo motor.

    A interface gráfica utiliza `registros` e `esperas` para construir
    a tabela final e o Gantt animado. A CLI/Output Writer utiliza os tempos
    médios e o diagrama em string.
    """
    nome_algoritmo: str
    tt_medio: float
    tw_medio: float
    trocas_contexto: int
    diagrama: str
    # Cada posição é um segundo: ID na CPU e IDs presentes antes de executar.
    registros: tuple[tuple[str | None, frozenset[str]], ...] = ()
    # Pares (ID, espera total em segundos), na ordem original da entrada.
    esperas: tuple[tuple[str, int], ...] = ()


def calcular_tempos(processos: Sequence[Processo]) -> tuple[float, float, tuple[tuple[str, int], ...]]:
    """Calcula tt_medio, tw_medio e a tupla de esperas.
    
    Fórmulas (baseadas nos slides da disciplina):
        - Turnaround (tt) = instante_termino - instante_criacao
        - Espera (tw) = turnaround - duração (tempo_processamento)
        - Média = soma / quantidade
    """
    if not processos:
        raise ValueError("Não é possível calcular tempos médios para uma lista vazia de processos.")

    soma_tt = 0
    soma_tw = 0
    esperas_list = []

    for p in processos:
        if not p.finalizado:
            raise ValueError(f"Processo {p.id} não finalizou. Não é possível calcular as métricas.")

        termino = int(p.instante_termino)  # type: ignore[arg-type]
        tt = termino - p.instante_criacao
        tw = tt - p.tempo_processamento

        soma_tt += tt
        soma_tw += tw
        esperas_list.append((p.id, tw))

    n = len(processos)
    return (soma_tt / n, soma_tw / n, tuple(esperas_list))


def contar_trocas_contexto(execucoes: Sequence[str | None]) -> int:
    """Conta as trocas de contexto a partir do histórico de uso da CPU."""
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
    registros: Sequence[tuple[str | None, frozenset[str]]] = (),
) -> ResultadoSimulacao:
    """Função de conveniência que consolida todas as saídas do motor."""
    tt_medio, tw_medio, esperas = calcular_tempos(processos)
    trocas = contar_trocas_contexto(execucoes)

    return ResultadoSimulacao(
        nome_algoritmo=nome_algoritmo,
        tt_medio=tt_medio,
        tw_medio=tw_medio,
        trocas_contexto=trocas,
        diagrama=diagrama.renderizar(),
        registros=tuple(registros),
        esperas=esperas,
    )
