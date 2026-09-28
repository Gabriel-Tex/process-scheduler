"""
Escalonador Round-Robin (nome interno: 'rr').

Algoritmo: preemptivo por esgotamento de quantum.
Mecânica:
    - Mantém uma fila circular (collections.deque) de processos prontos.
    - Processos que chegam são adicionados ao final da fila.
    - A cada tick, o processo no front da fila executa.
    - ao_finalizar_tick() decrementa o contador de quantum do processo em execução.
      Quando o quantum se esgota e o processo ainda não terminou, ele é movido para
      o final da fila (yield) e o próximo assume.
    - Não usa EscalonadorSelecao — usa deque próprio.

Parâmetro necessário (vindo de Configuracao):
    quantum: int  — fatia de tempo por processo

Validação manual esperada (dataset Seção 3, quantum=2):
    tt médio = 8,4 | tw médio = 5,6 | trocas de contexto = 7
"""
