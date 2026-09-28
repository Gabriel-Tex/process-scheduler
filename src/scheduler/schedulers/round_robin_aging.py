"""
Escalonador Round-Robin com Prioridade e Envelhecimento (nome interno: 'rr_prio_aging').

Algoritmo: preemptivo somente nas fronteiras de quantum (sem preempção mid-quantum).
Mecânica:
    - Usa heap de prioridade (heapq) indexado por prioridade_dinamica.
    - A cada início de quantum, seleciona_proximo() escolhe o processo com MAIOR
      prioridade_dinamica dentre os prontos (sem preempção durante o quantum).
    - ao_finalizar_tick() decrementa o contador de quantum:
        * Para processos AGUARDANDO (PRONTO, não em execução): prioridade_dinamica += aging
        * Para o processo em execução ao fim do quantum: prioridade_dinamica = prioridade_estatica
          (reset — volta à prioridade original).
    - Processos que chegam entram com prioridade_dinamica = prioridade_estatica.
    - Não usa EscalonadorSelecao — usa heap próprio.

Parâmetros necessários (vindo de Configuracao):
    quantum: int  — fatia de tempo por processo
    aging:   int  — incremento de prioridade por tick de espera

Validação manual esperada (dataset Seção 3):
    tt ≈ 5,8 | tw ≈ 3,0 (valores aproximados; só batem exatamente com quantum=1)

Suposição documentada: maior valor numérico = maior prioridade.
"""
