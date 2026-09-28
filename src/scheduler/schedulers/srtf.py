"""
Escalonador SRTF — Shortest Remaining Time First.

Algoritmo: preemptivo.
Chave de seleção: menor tempo_restante, reavaliada a cada tick.
Desempate: regra centralizada em escalonadores/base.py.

Herda de EscalonadorSelecao:
    - chave(p) = p.tempo_restante
    - preemptivo = True

Com preemptivo=True, selecionar_proximo() é chamado a cada tick mesmo que já
haja um processo na CPU; se outro processo tiver menor tempo_restante, ocorre
preempção (conta como troca de contexto).

Validação manual esperada (dataset da Seção 3 do contexto):
    tt médio = 5,4 | tw médio = 2,6 | trocas de contexto = 5
"""
