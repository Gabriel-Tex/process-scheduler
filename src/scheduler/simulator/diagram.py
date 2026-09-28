"""
Diagrama de tempo da simulação — DiagramaTempo.

Responsabilidades:
    - Acumular, tick a tick, o estado de cada processo.
    - Produzir a representação textual vertical do diagrama ao final.

Formato de saída (uma linha por tick, colunas = processos na ordem de ID):
    '##'  — processo executando naquele tick
    '--'  — processo PRONTO (já chegou, não terminou, não está na CPU)
    '  '  — processo ainda não chegou OU já terminou (célula em branco)

Interface pública:
    DiagramaTempo.registrar(tick: int, processos: list[Processo], em_execucao: Processo | None) -> None
        Chamado pelo motor a cada tick.

    DiagramaTempo.render() -> str
        Retorna a string formatada completa do diagrama, pronta para impressão.

Nota de design:
    DiagramaTempo não faz lógica de escalonamento — recebe os estados prontos e
    apenas os armazena/formata. Também é a fonte de dados para o Gantt animado da GUI.
"""
