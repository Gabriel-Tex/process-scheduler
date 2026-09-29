"""
Configuração da simulação.

Armazena os parâmetros lidos de config/config.txt (quantum e aging).
Embora só os algoritmos Round-Robin usem esses valores, a configuração é
sempre lida e repassada a todos os escalonadores para manter a interface
do motor uniforme.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Configuracao:
    """
    Parâmetros globais da simulação, vindos do arquivo de configuração.

    quantum: fatia de tempo do Round-Robin (inteiro > 0).
    aging: incremento de prioridade dinâmica por quantum de espera,
        usado pelo RR+envelhecimento (pd_i ← pd_i + α).
    """

    quantum: int = 2
    aging: int = 1
