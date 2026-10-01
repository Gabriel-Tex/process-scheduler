# Simulador de Escalonamento de Processos

Este projeto é um simulador discreto de algoritmos de escalonamento de processos em Sistemas Operativos, desenvolvido em Python. O simulador avança o relógio de forma unitária (tick-a-tick) e recolhe métricas e relatórios gráficos de execução.

Atualmente, dispõe de uma Interface Gráfica interativa construída com Tkinter, onde é possível visualizar a simulação passo-a-passo através de um diagrama de Gantt animado.

## 🚀 Como Executar

**Requisitos:**
- Python 3.10 ou superior.
- Biblioteca padrão de Python (com suporte a `tkinter` para a GUI).
- Sem dependências externas.

Para executar a Interface Gráfica, corra a partir da raiz do projeto:
```bash
python -m src.scheduler.gui
```

Para executar os testes automatizados da suíte:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

Opcionalmente, se tiver o pacote gerado (`SimuladorEscalonamento.pyz`), pode executar:
```bash
python SimuladorEscalonamento.pyz
```

## 🏗 Arquitetura do Projeto

O projeto segue princípios rigorosos de desacoplamento, separação de responsabilidades (SOLID) e funções puras:

1. **Domínio (`src/scheduler/domain/`)**: Contém as entidades centrais `Processo`, `StatusProcesso` e `Configuracao`. As classes usam `@dataclass` separando campos estáticos (entrada) de variáveis dinâmicas de controlo (tempo restante, prioridade, término, etc). Independe de qualquer outro módulo.
2. **Escalonadores (`src/scheduler/schedulers/`)**: Políticas que implementam a interface `EscalonadorBase` (métodos de *hook* `ao_chegar`, `selecionar_proximo`, `ao_finalizar_tick`). Uma fábrica (`factory.py`) cataloga os algoritmos sem instanciar conhecimento prévio.
3. **Motor Discreto (`src/scheduler/simulator/engine.py`)**: Controla a passagem do tempo. Desconhece a lógica concreta dos escalonadores. Processa as chegadas, gere a preempção baseada nas transições de processo, constrói os relatórios e regista métricas tick-a-tick.
4. **Cálculo de Métricas (`src/scheduler/simulator/result.py`)**: Calcula tempos de turnaround (`tt`), espera (`tw`), contagem de trocas de contexto e aglomera a visualização via funções puras.
5. **Apresentação Gráfica (`src/scheduler/gui/`)**: Separação em serviços, modelo e controladores. `ServicoReal` atua como ponte com a simulação do motor numa thread isolada, despachando os eventos para renderização de uma matriz Gantt sem corromper ou invadir objetos de domínio da simulação.

## 📚 Teoria e Convenções Adotadas

Como alguns aspetos na literatura podem ser ambíguos, estas são as interpretações teóricas implementadas de modo rigoroso:

- **Trocas de Contexto**: Uma troca é contabilizada **apenas** em transições consecutivas diretas entre dois processos *diferentes*. Sair do estado ocioso para executar ou deixar um processo para ficar em repouso não conta como troca.
- **Espera e Turnaround**: 
  - `Turnaround` (Tempo de vida) = `Término - Instante de Criação`.
  - `Espera (tw)` = `Turnaround - Duração Original (Tempo de processamento)`.
- **Preempção**: Interromper o processo caso chegue um novo em estado PRONTO com prioridade maior ou num quantum que expire.
- **Round-Robin com Prioridade e Envelhecimento**: Aumentar a prioridade (*aging*) das tarefas preteridas acontece **apenas** quando se encerra um quantum completo. Assim, trocas prematuras do escalonador ou entradas em CPU ociosa impedem uma inflação indevida da prioridade. Para resolução de empates adota-se os seguintes critérios de primazia: a) Processo em execução atual; b) Menor tempo restante; c) Sorteio aleatório fixo reproduzível.
- **Tratamento Fila FIFO**: No RR clássico, as chegadas de novos processos no instante `t` entram na fila antes do re-enfileiramento do processo que viu o seu quantum terminar no instante `t`.

> Mais detalhes de design interno estão disponíveis em `docs/decisoes_implementacao.md`.

## 🚧 O Que Falta e Próximos Passos (Backlog)

Atualmente, o **Épico 1** (Núcleo) e o **Épico 3** (GUI e Round-Robin) encontram-se em avançado estado de fusão. Contudo, faltam os seguintes elementos (a cargo do Épico 2 e das pendências de orquestração do Épico 1):

1. **Restantes Algoritmos do Épico 2**: Implementar as restantes estratégias concretas de `EscalonadorBase`: 
   - `SJF` (Shortest Job First)
   - `SRTF` (Shortest Remaining Time First)
   - `Prioridade Cooperativa`
   - `Prioridade Preemptiva`
2. **Saída Formatada Padrão (stdout)**: Implementar efetivamente o modo texto formatado no ecrã (atualmente delineado em `src/scheduler/io/output_writer.py`) que imprima a tabela comparativa.
3. **CLI Orquestradora completa**: O `src/scheduler/cli/app_cli.py` está desenhado, mas precisa ser invocado e preenchido para suportar uma simulação puramente de linha de comando usando `--config` e ler o stdin via os *parsers* construídos na História 1.3 e 1.4 (`io/input_reader.py` e `io/config_reader.py`).
