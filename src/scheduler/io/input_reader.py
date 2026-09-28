"""
Leitura de processos via stdin — LeitorEntrada.

Responsabilidades:
    - Parsear cada linha de stdin no formato:  <instante_criacao> <duracao> <prioridade>
    - Atribuir IDs sequenciais na ordem de leitura (P1, P2, …), independente da ordem
      de instante_criacao.
    - Validar cada campo:
        * instante_criacao >= 0
        * duracao > 0
        * prioridade >= 0
    - Levantar ValueError com mensagem clara (número da linha + campo inválido) em caso
      de entrada mal-formada.
    - Retornar uma lista de EspecificacaoProcesso (dados brutos, sem estado de simulação)
      que será convertida em List[Processo] antes de cada execução de algoritmo.

Nota: a entrada NÃO é necessariamente ordenada por instante_criacao — o motor
deve lidar com isso; o leitor apenas garante a validação e o ID sequencial.
"""
