"""Controlador testável sem janela. Valida usando os leitores do núcleo."""

from io import StringIO

from src.scheduler.io.input_reader import ler_processos
from src.scheduler.io.config_reader import ler_configuracao
from .models import ResultadoGUI
from .services import ServicoSimulacao, ALGORITMOS_PREEMPTIVOS


class ControladorGUI:
    def __init__(self, servico: ServicoSimulacao):
        self.servico = servico
        self.resultados: list[ResultadoGUI] = []

    @staticmethod
    def validar_processos(texto: str):
        processos = ler_processos(StringIO(texto))
        if not processos:
            raise ValueError("Adicione pelo menos um processo.")
        return processos

    @staticmethod
    def validar_config(quantum: str, aging: str):
        return ler_configuracao(StringIO(f"quantum:{quantum}\naging:{aging}"))

    def executar(self, texto: str, quantum: str, aging: str,
                 algoritmos: list[str], permitir_preempcao: bool = True) -> list[ResultadoGUI]:
        processos = self.validar_processos(texto)
        config = self.validar_config(quantum, aging)
        disponiveis = self.servico.listar_algoritmos()
        if not algoritmos:
            raise ValueError("Selecione pelo menos um algoritmo.")
        if any(nome not in disponiveis for nome in algoritmos):
            raise ValueError("Há um algoritmo selecionado que não está disponível.")
        if not permitir_preempcao and ALGORITMOS_PREEMPTIVOS.intersection(algoritmos):
            raise ValueError("Preempção desativada: selecione um algoritmo cooperativo.")
        resultados = self.servico.executar(processos, config, algoritmos)
        self.resultados = resultados
        return resultados
