"""
PENDENTE: este arquivo contém apenas planejamento, não implementação.

Escalonador SJF — Shortest Job First.

Algoritmo: não-preemptivo.
Chave de seleção: menor duracao (tempo total, não o restante — decisão tomada
    no momento em que o processo entra na CPU e não muda até ele terminar).
Desempate: regra centralizada em escalonadores/base.py.

Herda de EscalonadorSelecao:
    - chave(p) = p.duracao
    - preemptivo = False

Validação manual esperada (dataset da Seção 3 do contexto):
    tt médio = 5,8 | tw médio = 3,0 | trocas de contexto = 4
"""
