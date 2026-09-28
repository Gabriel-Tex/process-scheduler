"""
Interface abstrata de todos os escalonadores + função de desempate centralizada.

EscalonadorBase (ABC):
    Contrato que cada algoritmo concreto deve implementar.

    ao_chegar(processo, tempo) -> None
        Chamado pelo motor no tick em que instante_criacao == tempo.
        O algoritmo deve inserir o processo em sua estrutura interna de fila.

    selecionar_proximo(tempo, em_execucao) -> Processo | None
        Chamado a cada tick pelo motor para decidir quem ocupa a CPU.
        Retorna None quando não há processo pronto.

    ao_finalizar_tick(tempo, em_execucao) -> None  [hook opcional]
        Chamado ao final de cada tick. Usado por RR (contagem de quantum) e
        RR+envelhecimento (incremento de prioridade dinâmica).

    ao_finalizar_processo(processo, tempo) -> None  [hook opcional]
        Chamado quando um processo tem tempo_restante == 0. Permite limpeza
        de estruturas internas nos algoritmos que precisam disso.

Função desempatar(candidatos, em_execucao, rng) -> Processo:
    Regra única de desempate, compartilhada por TODOS os algoritmos:
        1. Processo que já está na CPU (evita troca desnecessária).
        2. Menor tempo_restante.
        3. Aleatório — usa `rng` (random.Random injetado) para determinismo em testes.
    Deve ser chamada pelos algoritmos sempre que houver dois ou mais candidatos
    com chave primária de seleção igual. NUNCA duplicar esta lógica nos módulos
    concretos de escalonadores.
"""
