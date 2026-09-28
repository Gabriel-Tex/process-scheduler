"""
Dataclass de resultado de uma simulação — ResultadoSimulacao.

Responsabilidades:
    - Agregar todas as métricas calculadas após a execução de UM algoritmo.
    - Ser imutável após a criação (frozen dataclass ou similar).

Campos:
    nome_algoritmo    : str            — ex.: 'FCFS', 'Round-Robin'
    tt_medio          : float          — turnaround time médio (tempo de execução total médio)
    tw_medio          : float          — tempo de espera médio
    trocas_contexto   : int            — número de trocas de contexto contabilizadas pelo motor
    diagrama          : str            — saída renderizada de DiagramaTempo.render()

Cálculos (responsabilidade do MotorSimulacao ao popular este objeto):
    turnaround_i = instante_conclusao_i - instante_criacao_i
    espera_i     = turnaround_i - duracao_i
    tt_medio     = mean(turnaround_i)
    tw_medio     = mean(espera_i)
"""
