"""
Fábrica de escalonadores — padrão Factory.

Responsabilidades:
    - Manter o mapa de nomes (str) -> construtores de escalonadores concretos.
    - Ser o ÚNICO ponto do código onde classes concretas de escalonadores são
      instanciadas. CLI e GUI nunca importam classes de algoritmos diretamente.

Mapa registrado (nome interno -> classe):
    'fcfs'         -> FCFS
    'sjf'          -> SJF
    'srtf'         -> SRTF
    'prioc'        -> PrioridadeCooperativa
    'priop'        -> PrioridadePreemptiva
    'rr'           -> RoundRobin
    'rr_prio_aging'-> RoundRobinEnvelhecimento

Função principal:
    criar_escalonador(nome: str, config: Configuracao, rng: random.Random | None)
        -> EscalonadorBase
    Levanta ValueError com mensagem clara se o nome não for reconhecido.

Constante utilitária:
    ALGORITMOS_DISPONIVEIS: list[str]  — lista ordenada de todos os nomes válidos,
    usada pela CLI para exibir opções e para iterar os 7 algoritmos no modo padrão.
"""
