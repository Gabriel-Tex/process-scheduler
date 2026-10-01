"""Ponte entre a GUI e o núcleo; demonstração explicitamente separada."""

from __future__ import annotations

import importlib
import random
from typing import Protocol

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers import factory
from src.scheduler.simulator.diagram import DiagramaTempo
from .models import ResultadoGUI, TickGUI


NOMES_ALGORITMOS = {
    "fcfs": "FCFS", "sjf": "SJF", "srtf": "SRTF",
    "prioc": "Prioridade cooperativa", "priop": "Prioridade preemptiva",
    "rr": "Round-Robin", "rr_prio_aging": "Round-Robin + envelhecimento",
}

# Classificação oficial: o filtro da GUI não altera a política dos algoritmos.
ALGORITMOS_PREEMPTIVOS = frozenset({"rr", "rr_prio_aging", "srtf", "priop"})


class ServicoSimulacao(Protocol):
    def listar_algoritmos(self) -> list[str]: ...

    def executar(
        self, processos: list[Processo], config: Configuracao,
        algoritmos: list[str],
    ) -> list[ResultadoGUI]: ...


def adaptar_resultado(resultado: object, ids: tuple[str, ...]) -> ResultadoGUI:
    """Converte o contrato do motor, com registros opcionais (id, presentes).

    O épico 1 pode acrescentar ``registros`` sem importar nada da GUI.
    Não acessamos atributos privados de DiagramaTempo.
    """
    registros = getattr(resultado, "registros", None)
    ticks = None if registros is None else tuple(
        TickGUI(executando, frozenset(presentes))
        for executando, presentes in registros
    )
    return ResultadoGUI(
        nome_algoritmo=resultado.nome_algoritmo,
        tt_medio=resultado.tt_medio,
        tw_medio=resultado.tw_medio,
        trocas_contexto=resultado.trocas_contexto,
        diagrama=resultado.diagrama,
        ids_processos=ids,
        registros=ticks,
        esperas=tuple(getattr(resultado, "esperas", ())),
    )


class ServicoReal:
    def listar_algoritmos(self) -> list[str]:
        return factory.listar_algoritmos()

    @staticmethod
    def _classe_motor():
        nome_modulo = "src.scheduler.simulator.engine"
        try:
            modulo = importlib.import_module(nome_modulo)
        except ModuleNotFoundError as erro:
            # Ausência do motor é prevista; dependência quebrada dentro dele não é.
            if erro.name == nome_modulo:
                return None
            raise
        return getattr(modulo, "MotorSimulacao", None)

    def motivo_indisponivel(self) -> str | None:
        if self._classe_motor() is None:
            return "A execução será liberada quando o motor de simulação do épico 1 estiver integrado."
        if not self.listar_algoritmos():
            return "Nenhum algoritmo foi registrado na fábrica."
        return None

    def executar(self, processos, config, algoritmos) -> list[ResultadoGUI]:
        motivo = self.motivo_indisponivel()
        if motivo:
            raise RuntimeError(motivo)
        classe_motor = self._classe_motor()
        resultados = []
        for nome in algoritmos:
            # Reconstruir entradas; nunca reutilizar processos já executados.
            novos = [Processo(p.id, p.instante_criacao, p.tempo_processamento,
                              p.prioridade_estatica) for p in processos]
            configuracao = Configuracao(config.quantum, config.aging)
            escalonador = factory.criar(nome, configuracao, random.Random(0))
            resultado = classe_motor().executar(novos, escalonador, configuracao)
            resultados.append(adaptar_resultado(resultado, tuple(p.id for p in novos)))
        return resultados


class ServicoDemonstrativo:
    """Fixture visual fixa. Nunca lê a tela nem executa um escalonador."""

    @staticmethod
    def carregar() -> list[ResultadoGUI]:
        ids = ("P1", "P2", "P3", "P4")
        sequencia = ("P1", "P1", "P2", "P2", "P3", "P3", "P1",
                     "P1", "P4", "P4", "P3", "P3", "P1", "P4")
        chegadas = (0, 0, 1, 3)
        terminos = (13, 4, 12, 14)
        ticks = tuple(TickGUI(pid, frozenset(
            p for p, chegada, termino in zip(ids, chegadas, terminos)
            if chegada <= t < termino
        )) for t, pid in enumerate(sequencia))
        diagrama = DiagramaTempo(ids)
        for tick in ticks:
            diagrama.registrar_tick(tick.executando, tick.presentes)
        return [ResultadoGUI("Exemplo ilustrativo • quantum 2", 9.75, 6.25, 7,
                             diagrama.renderizar(), ids, ticks,
                             (("P1", 8), ("P2", 2), ("P3", 7), ("P4", 8)))]
