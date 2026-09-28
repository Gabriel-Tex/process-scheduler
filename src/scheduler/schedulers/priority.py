"""
Escalonadores por Prioridade Estática — cooperativo e preemptivo.

Dois algoritmos neste módulo (compartilham a mesma base parametrizável):

PrioridadeCooperativa  (nome interno: 'prioc')
    Algoritmo: não-preemptivo.
    Chave de seleção: maior prioridade_estatica.
    Herda de EscalonadorSelecao:
        - chave(p) = -p.prioridade_estatica   # negativo p/ usar min-heap / sorted()
        - preemptivo = False
    Validação manual (dataset Seção 3):
        tt médio = 6,6 | tw médio = 3,8 | trocas de contexto = 4

PrioridadePreemptiva  (nome interno: 'priop')
    Algoritmo: preemptivo.
    Chave de seleção: maior prioridade_estatica, reavaliada a cada tick.
    Herda de EscalonadorSelecao:
        - chave(p) = -p.prioridade_estatica
        - preemptivo = True
    Validação manual (dataset Seção 3):
        tt médio = 5,6 | tw médio = 2,8 | trocas de contexto = 6

Convenção de prioridade:
    Maior valor numérico = maior prioridade.
    Suposição documentada em docs/decisoes_implementacao.md.
"""
