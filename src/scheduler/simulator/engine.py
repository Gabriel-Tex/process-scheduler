"""
Motor de simulação por tick discreto — MotorSimulacao.

Responsabilidades:
    - Executar o laço de simulação (tick a tick) para UM escalonador.
    - Ser agnóstico ao algoritmo concreto — só conhece EscalonadorBase.
    - Produzir um ResultadoSimulacao ao final.

Laço principal (a cada tick t = 0, 1, 2, …, até todos os processos finalizarem):
    1. Processar chegadas: para cada processo com instante_criacao == t,
       chamar escalonador.ao_chegar(processo, t) e marcar como PRONTO.
    2. Selecionar próximo: em_execucao = escalonador.selecionar_proximo(t, em_execucao)
    3. Executar 1 segundo: decrementar tempo_restante do processo em execução (se houver).
    4. Registrar diagrama: informar DiagramaTempo o estado de cada processo neste tick.
    5. Contabilizar troca de contexto: se o processo que ocupa a CPU mudou em relação
       ao tick anterior (e não é a primeira CPU-ocupação da simulação), incrementar contador.
    6. Hook: escalonador.ao_finalizar_tick(t, em_execucao)
    7. Verificar finalização: se tempo_restante == 0, marcar FINALIZADO, registrar
       instante de conclusão, chamar escalonador.ao_finalizar_processo().
    8. Avançar t.

Interface pública:
    MotorSimulacao.executar(
        processos: list[Processo],     # cópias frescas — nunca reutilizar entre algoritmos
        escalonador: EscalonadorBase,
        config: Configuracao,
    ) -> ResultadoSimulacao

Invariante: este módulo nunca importa nenhuma classe concreta de escalonador.
"""
