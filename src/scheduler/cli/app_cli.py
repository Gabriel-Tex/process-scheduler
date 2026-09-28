"""
Interface de linha de comando — AppCLI.

Responsabilidades:
    - Definir e processar argumentos via argparse.
    - Orquestrar o fluxo completo: leitura -> execução -> saída.
    - Ser o único lugar que "liga" todos os módulos.

Argumentos suportados:
    --config  PATH          Caminho para o arquivo de configuração
                            (padrão: config/config.txt relativo ao CWD)
    --algoritmo  NOME       Executar apenas um algoritmo específico.
                            Valores válidos: fcfs, sjf, srtf, prioc, priop, rr, rr_prio_aging
                            (padrão: executa os 7)
    --seed  INT             Semente para o random.Random usado no desempate.
                            Permite reprodutibilidade em testes manuais.

Fluxo de execução:
    1. LeitorConfig.ler(config) -> Configuracao
    2. LeitorEntrada.ler(stdin) -> list[EspecificacaoProcesso]
    3. Para cada algoritmo selecionado:
        a. Criar cópias frescas de Processo a partir das especificações.
        b. FabricaEscalonadores.criar(nome, config, rng) -> EscalonadorBase
        c. MotorSimulacao.executar(processos, escalonador, config) -> ResultadoSimulacao
        d. EscritorSaida.imprimir_resultado(resultado)
    4. Se mais de um algoritmo: EscritorSaida.imprimir_tabela_comparativa(resultados)

Invariante: AppCLI não contém lógica de simulação — apenas orquestra.
"""
