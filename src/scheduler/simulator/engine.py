"""Motor de simulação discreto (tick a tick).

Orquestra a passagem do tempo, entrega processos ao escalonador,
registra quem executa a cada segundo e consolida o resultado final.
Não conhece a política interna de nenhum algoritmo concreto.
"""

from __future__ import annotations

import copy
from collections.abc import Sequence

from src.scheduler.domain.process import Processo, StatusProcesso
from src.scheduler.schedulers.base import EscalonadorBase
from .diagram import DiagramaTempo
from .result import ResultadoSimulacao, construir_resultado


def _validar_entrada(processos: Sequence[Processo]) -> None:
    """Verifica pré-condições antes de iniciar a simulação."""
    if not processos:
        raise ValueError("Nenhum processo para simular.")
    ids = [p.id for p in processos]
    if len(set(ids)) != len(ids):
        raise ValueError("IDs de processos duplicados encontrados.")


def simular(
    processos: Sequence[Processo],
    escalonador: EscalonadorBase,
    nome_algoritmo: str,
) -> ResultadoSimulacao:
    """Executa a simulação tick a tick e devolve o resultado consolidado.

    Trabalha sobre cópias dos processos para não mutar a entrada,
    permitindo que a mesma lista sirva para múltiplos algoritmos.
    """
    _validar_entrada(processos)

    copias = [copy.deepcopy(p) for p in processos]
    ids_em_ordem = [p.id for p in copias]
    diagrama = DiagramaTempo(ids_em_ordem)

    execucoes: list[str | None] = []
    registros: list[tuple[str | None, frozenset[str]]] = []

    em_execucao: Processo | None = None
    t = 0

    # Limite para detectar escalonadores com bug (loop infinito).
    limite = (max(p.instante_criacao for p in copias)
              + sum(p.tempo_processamento for p in copias) + 100)

    while any(not p.finalizado for p in copias):
        if t > limite:
            raise RuntimeError(
                f"Limite de segurança atingido no instante {t}. "
                "Possível loop infinito no escalonador."
            )

        # 1. Chegadas: processos criados neste instante entram na fila.
        for p in copias:
            if p.instante_criacao == t:
                p.status = StatusProcesso.PRONTO
                p.prioridade_dinamica = p.prioridade_estatica
                escalonador.ao_chegar(p, t)

        # 2. Presentes: quem já chegou e ainda não terminou.
        presentes = [p for p in copias
                     if p.instante_criacao <= t and not p.finalizado]
        ids_presentes = frozenset(p.id for p in presentes)

        # 3. Seleção: o escalonador decide quem ocupa a CPU.
        escolhido = escalonador.selecionar_proximo(t, em_execucao)

        if escolhido is not None:
            if escolhido not in copias:
                raise RuntimeError(
                    f"Tick {t}: escalonador escolheu processo "
                    "fora da simulação."
                )
            if escolhido.finalizado or escolhido.instante_criacao > t:
                raise RuntimeError(
                    f"Tick {t}: escalonador escolheu processo "
                    f"que não está pronto (id={escolhido.id})."
                )
        elif presentes:
            raise RuntimeError(
                f"Tick {t}: escalonador devolveu None "
                "havendo processos prontos."
            )

        # 4. Execução: preempção do anterior e avanço do escolhido.
        if escolhido is not None:
            if (em_execucao is not None
                    and em_execucao is not escolhido
                    and not em_execucao.finalizado):
                em_execucao.status = StatusProcesso.PRONTO
            if escolhido.instante_inicio is None:
                escolhido.instante_inicio = t
            escolhido.status = StatusProcesso.EXECUTANDO
            escolhido.executar_um_tick()

        # 5. Término: marca o instante de finalização.
        if escolhido is not None and escolhido.tempo_restante == 0:
            escolhido.instante_termino = t + 1
            escolhido.status = StatusProcesso.FINALIZADO

        # 6. Hook: notifica o algoritmo (quantum, aging, etc.).
        escalonador.ao_finalizar_tick(t, escolhido)

        # 7. Registro: grava estado do tick para diagrama e métricas.
        pid = escolhido.id if escolhido is not None else None
        execucoes.append(pid)
        registros.append((pid, ids_presentes))
        diagrama.registrar_tick(executando=pid, presentes=ids_presentes)

        # 8. Atualiza referência do processo em execução.
        if escolhido is not None and not escolhido.finalizado:
            em_execucao = escolhido
        else:
            em_execucao = None

        t += 1

    return construir_resultado(
        nome_algoritmo=nome_algoritmo,
        processos=copias,
        execucoes=execucoes,
        diagrama=diagrama,
        registros=registros,
    )


class MotorSimulacao:
    """Wrapper de compatibilidade para a GUI (que usa a interface de classe)."""

    def executar(
        self,
        processos: list[Processo],
        escalonador: EscalonadorBase,
        configuracao: object,
    ) -> ResultadoSimulacao:
        nome = getattr(escalonador, "nome", type(escalonador).__name__)
        return simular(processos, escalonador, nome)
