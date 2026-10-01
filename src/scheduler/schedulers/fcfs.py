"""
PENDENTE: este arquivo contém apenas planejamento, não implementação.

Escalonador FCFS — First-Come, First-Served.

Algoritmo: não-preemptivo.
Chave de seleção: menor instante_criacao (ordem de chegada).
Desempate: regra centralizada em escalonadores/base.py.

Herda de EscalonadorSelecao (base parametrizável definida em base.py), que
implementa a lógica de "manter fila de prontos + selecionar por chave + flag
de preempção". FCFS apenas injeta:
    - chave(p) = p.instante_criacao
    - preemptivo = False

Validação manual esperada (dataset da Seção 3 do contexto):
    tt médio = 8,0 | tw médio = 5,2 | trocas de contexto = 4
"""
