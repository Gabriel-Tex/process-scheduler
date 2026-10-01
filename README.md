# Process Scheduler

Process Scheduler é um simulador de escalonamento de processos em Python, pensado para estudar e comparar algoritmos de escalonamento em Sistemas Operacionais. O objetivo principal é modelar a execução de processos em um ambiente discreto, avançando tick a tick, medindo desempenho e permitindo a comparação entre políticas como FCFS, SJF, SRTF, prioridade e Round Robin.

Este projeto foi desenvolvido como estudo acadêmico e como exercício de arquitetura de software: separação por camadas, domínio, simulador, escalonadores e interface de entrada/saída. Ele ainda está em desenvolvimento, e o README descreve tanto o estado atual quanto o que já foi estruturado para a próxima etapa de implementação.

## Status do projeto

O projeto está em fase de desenvolvimento ativo e não deve ser tratado como versão final. A estrutura principal já foi organizada em módulos bem definidos, incluindo:

- domínio de processos e configuração;
- fábrica de escalonadores;
- motor de simulação discreta;
- visualização em diagrama de tempo;
- leitura de entrada e configuração;
- documentação técnica e decisões de implementação.

Algumas partes da CLI e de certos algoritmos ainda estão em planejamento ou parcialmente implementadas, e a intenção deste README é documentar a arquitetura e o caminho de evolução do projeto com clareza.

## Objetivo

O simulador permite:

- representar processos com instantes de criação, duração, prioridade e estado;
- executar algoritmos de escalonamento em um ambiente discreto;
- comparar métricas como tempo médio de turnaround e espera;
- contabilizar trocas de contexto;
- gerar diagramas de execução para visualização da ordem de ocupação do processador;
- servir como base para estudos, exercícios e extensão futura para interface gráfica ou linha de comando.

## Requisitos

- Python 3.10+
- Biblioteca padrão do Python
- (Opcional, para GUI) biblioteca `tkinter`, normalmente disponível em instalações padrão do Python para Linux/macOS/Windows

Não há dependências externas obrigatórias nesse momento.

## Estrutura do projeto

```text
process-scheduler/
├── README.md
├── config/
│   └── config.txt
├── docs/
│   └── decisoes_implementacao.md
├── examples/
├── src/
│   └── scheduler/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       ├── domain/
│       ├── gui/
│       ├── io/
│       ├── schedulers/
│       └── simulator/
├── tests/
├── iniciar_interface.py
├── user-stories.md
├── SimuladorEscalonamento.pyz
└── requirements.txt
```

## Visão geral da arquitetura

O projeto foi pensado em camadas para separar responsabilidade e reduzir acoplamento.

### 1. Camada de domínio

Diretório: `src/scheduler/domain/`

Aqui ficam as entidades centrais:

- `Processo`: modela uma tarefa com id, instante de criação, duração, prioridade, tempo restante, status e timestamps de início/fim.
- `StatusProcesso`: enumeração com os estados do ciclo de vida da tarefa.
- `Configuracao`: guarda parâmetros globais da simulação, principalmente quantum e aging.

Essa camada é o coração do sistema, e foi construída para ser independente das regras de escalonamento e da interface do usuário.

### 2. Camada de escalonadores

Diretório: `src/scheduler/schedulers/`

Aqui ficam as políticas de escalonamento, cada uma respeitando uma interface base comum. A ideia é que o motor de simulação não conheça algoritmos concretos, apenas a abstração de escalonamento.

Algoritmos previstos/estruturados:

- FCFS
- SJF
- SRTF
- Prioridade cooperativa
- Prioridade preemptiva
- Round Robin
- Round Robin com prioridade e envelhecimento

A fábrica `factory.py` centraliza o registro e a criação de algoritmos por nome.

### 3. Motor de simulação

Diretório: `src/scheduler/simulator/`

O motor é responsável pelo loop principal da simulação:

1. processa chegadas;
2. consulta o escalonador qual processo deve executar;
3. executa um tick;
4. atualiza o estado do sistema;
5. coleta dados para o diagrama e para as métricas.

Ele é independente do algoritmo concreto aplicado, o que torna a simulação mais reutilizável e testável.

### 4. Entrada e saída

Diretório: `src/scheduler/io/`

O projeto separa a leitura de entrada e configuração da lógica de simulação em módulos específicos:

- leitura de processos via entrada padrão;
- leitura de configurações via arquivo;
- escrita de resultados em formato textual para terminal;
- geração de representações por algoritmo.

### 5. GUI e CLI

Diretórios:

- `src/scheduler/gui/`
- `src/scheduler/cli/`

A intenção é que a interface gráfica e a linha de comando compartilhem o mesmo motor de simulação. Assim, tanto a CLI quanto a GUI usam o mesmo núcleo, evitando duplicação de lógica de negócio.

## Como rodar o projeto

### Ambiente local

A partir da raiz do projeto, é possível validar a estrutura do pacote com:

```bash
PYTHONPATH=src python -m compileall src
```

Esse comando foi usado como validação de integridade do projeto e confirma que o pacote compila corretamente.

### Execução da interface gráfica

O projeto inclui um arquivo de inicialização para GUI:

```bash
python iniciar_interface.py
```

Esse é o ponto de entrada previsto para a execução da interface visual, conforme o projeto foi organizado.

### Execução da CLI

A interface de linha de comando orquestra a leitura, execução e formatação dos resultados para os algoritmos. O fluxo principal é:

```bash
PYTHONPATH=src python -m scheduler --config config/config.txt < examples/exemplo_pdf.txt
```

Também é possível especificar a execução de apenas um algoritmo e fixar a semente aleatória para o desempate:

```bash
PYTHONPATH=src python -m scheduler --algoritmo rr --semente 7 < examples/dataset_slides.txt
```

## Entrada de dados

O simulador trabalha com um formato simples de processo:

```text
instante_criacao duracao prioridade
```

Exemplo:

```text
0 5 2
1 3 1
2 4 3
```

A interpretação é:

- instante de criação: quando o processo entra no sistema;
- duração: tempo de processamento necessário;
- prioridade: valor usado por algoritmos prioritários.

A configuração do sistema pode ser lida de um arquivo como:

```text
quantum:2
aging:1
```

## Teoria dos escalonadores

Este projeto é um estudo prático de algoritmos clássicos de escalonamento.

### FCFS

First-Come, First-Served. Os processos são executados na ordem de chegada. É simples e previsível, mas pode gerar longos tempos de espera quando há processos longos chegando primeiro.

### SJF

Shortest Job First. Seleciona o processo com menor tempo de processamento. Reduz o tempo médio de espera, mas exige conhecimento do tempo de execução do processo.

### SRTF

Shortest Remaining Time First. Variante preemptiva do SJF. Se um processo com menor tempo restante chega, ele pode interromper a execução atual.

### Prioridade

A prioridade pode ser cooperativa ou preemptiva. Em geral, processos com maior prioridade são atendidos primeiro, mas podem causar starvation em ambiente sem compensação.

### Round Robin

Round Robin usa fatia de tempo (quantum). Cada processo executa por um intervalo fixo e, se não terminar, retorna para a fila. É útil para justiça de uso do processador.

### Round Robin com envelhecimento

Essa variação adiciona aumento de prioridade dinâmica para processos que aguardam por muito tempo, mitigando starvation e equilibrando justiça e prioridade.

## Métricas calculadas

A comparação entre algoritmos costuma ser feita usando métricas como:

- turnaround: tempo total do processo desde sua criação até sua conclusão;
- waiting time: tempo que o processo ficou pronto aguardando a CPU;
- trocas de contexto: quantas vezes a CPU mudou de processo;
- diagrama de execução: representação visual do uso do processador ao longo do tempo.

A fórmula básica adotada é:

- turnaround = instante de término - instante de criação
- waiting time = turnaround - tempo de processamento

A ideia é comparar o comportamento dos algoritmos sob o mesmo conjunto de processos.

## Diagrama de execução

O projeto também usa uma representação visual do uso do processador ao longo dos ticks. O objetivo é mostrar, em uma grade temporal, quais processos estavam executando, quais estavam prontos e quais ainda não haviam chegado.

Esse recurso é especialmente útil para:

- comparar políticas de escalonamento;
- entender troca de contexto;
- analisar quando a CPU ficou ociosa;
- validar se o algoritmo atende às regras esperadas.

## Estado atual e roadmap

O projeto já possui a base estrutural bem definida, mas ainda está incompleto em relação ao estado de produto final. Os pontos principais do roadmap são:

### Pronto ou em andamento

- estrutura modular do projeto;
- domínio de processos e configuração;
- motor de simulação discreto;
- fábrica de escalonadores;
- diagrama de tempo;
- documentação de decisões de implementação;
- organização dos testes e artefatos de suporte.

### Ainda pendentes ou parcialmente implementados

- CLI completa e interativa;
- execução de todos os algoritmos concretos;
- saída formatada em terminal;
- integração final entre leitura de dados, execução e apresentação;
- refinamento de GUI e visualização;
- ajustes finais de usabilidade e validação de cenários reais.

## Boas práticas adotadas

O projeto foi organizado seguindo algumas boas práticas de engenharia de software:

- separação clara por camadas;
- desacoplamento entre domínio, escalonamento e interface;
- regras centralizadas para desempate e parametrização;
- objetos de configuração em dataclass;
- estrutura modular para facilitar manutenção e extensão;
- foco em comparabilidade entre algoritmos.

## Desafios e observações

Um projeto de escalonamento de processos exige atenção especial a detalhes como:

- checagem de processos que chegam em momentos diferentes;
- controle do estado do processo em cada tick;
- contagem correta de trocas de contexto;
- tratamento de quantum e envelhecimento;
- preempção em cenários de empate e prioridade;
- geração de resultados reproduzíveis e comparáveis.

Esses detalhes são o que tornam o tema relevante em Sistemas Operacionais e o que motivam a arquitetura do projeto.

## Contribuição

Este projeto é um estudo de arquitetura e algoritmo e pode ser expandido. Sugestões de melhorias incluem:

- completar a CLI;
- finalizar os algoritmos restantes;
- implementar testes automáticos mais completos;
- comparar resultados com cenários de referência;
- melhorar apresentação de métricas e gráficos.

## Licença

O projeto não define uma licença formal neste momento. Em desenvolvimento, ele é usado como base acadêmica e de estudo. Caso o projeto passe a ser compartilhado publicamente em outro contexto, a licença deve ser explicitada antes da distribuição.

## Observação final

Este README foi escrito como documentação do estado atual do projeto e como guia para manutenção e evolução futura. A arquitetura já foi organizada de forma sólida, mas o sistema ainda não deve ser considerado concluído: o foco de desenvolvimento contínuo está em finalizar a integração entre módulos e validar os algoritmos em cenários reais de simulação.
