"""Testes manuais do algoritmo FCFS.

Executar com:  python tests/test_fcfs.py

Dataset de referência (Seção 3 do contexto):
    T1: ingresso=0, duração=5, prioridade=2
    T2: ingresso=0, duração=2, prioridade=3
    T3: ingresso=1, duração=4, prioridade=1
    T4: ingresso=3, duração=1, prioridade=4
    T5: ingresso=5, duração=2, prioridade=5

Valores esperados:
    tt médio = 8,0
    tw médio = 5,2
    trocas de contexto = 4
"""
