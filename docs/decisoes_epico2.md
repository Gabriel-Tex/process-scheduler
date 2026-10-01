# Épico 2: algoritmos de seleção

## Base comum

Usei `EscalonadorPorChave`, derivada de `EscalonadorBase`, para compartilhar a lista de prontos, a seleção pelo menor valor e o desempate. Cada escalonador fornece uma função `chave` e informa se é preemptivo. Isso evita repetir a lógica da fila e da escolha nos cinco algoritmos.

A chave é sempre minimizada. FCFS usa o instante de criação, SJF usa `tempo_processamento` original e SRTF usa `tempo_restante` atual. Os algoritmos de prioridade usam `-prioridade_estatica`, pois a convenção é que o maior valor numérico significa maior prioridade.

## Seleção e desempate

Quando a chave empata, `desempatar` prefere primeiro o processo que já está na CPU, depois o de menor tempo restante e, se o empate continuar, escolhe aleatoriamente. A aleatoriedade recebe um `random.Random` opcional na construção dos escalonadores, permitindo fixar a semente nos testes.

Nos algoritmos cooperativos, se há um processo não finalizado em execução, a base o devolve sem compará-lo aos prontos. Nos preemptivos, o processo atual participa dos candidatos junto com a lista de prontos em cada seleção. Assim uma nova escolha pode interrompê-lo, mas um empate mantém a mesma instância na CPU.

A lista de prontos é uma `list[Processo]`: chegadas são anexadas e a base percorre os candidatos para encontrar a menor chave. A lista mantém as instâncias dos processos, sem armazenar cópias das chaves. O processo que está executando é passado separadamente em `em_execucao`; nos algoritmos preemptivos, ele é incluído entre os candidatos no momento da seleção.

## Responsabilidades e padrões

Os escalonadores apenas indicam qual processo deve executar; não contam trocas de contexto. A documentação de `MotorSimulacao` atribui essa contagem ao motor, comparando quem executa entre ticks. Porém, neste estado do repositório, `engine.py` contém apenas a descrição do ciclo, sem implementação executável. Portanto, as trocas ainda não foram verificadas por uma simulação integrada.

A função `chave` injetada cumpre o papel de uma estratégia de seleção, sem uma hierarquia de classes de estratégia. A fábrica em `factory.py` mantém um registro de nomes para construtores, usado para criar os escalonadores. O arquivo `app_cli.py` também contém apenas documentação, então a execução via CLI não está disponível para validação neste estado.