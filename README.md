# Simulador de Escalonamento de Processos

Projeto da disciplina de Sistemas Operacionais, em Python.

## Abrir a interface

Na raiz do repositório, em um terminal com Python **3.10 ou superior** e Tkinter:

```powershell
python -m src.scheduler.gui
```

Se o Windows disponibilizar Python pelo launcher, use `py -m src.scheduler.gui`.
Para verificar Tkinter: `python -m tkinter` deve abrir uma pequena janela de teste.
Não há dependências externas para a interface ou os testes.

1. Clique em **Carregar exemplo** ou cadastre os processos.
2. Ajuste quantum e aging, ou carregue o arquivo `config/config.txt`.
3. Clique em **Ver demonstração** para explorar a tabela e o diagrama.
4. Clique em **Reproduzir** ou **Avançar** para acompanhar os ticks.

**A demonstração usa dados fixos e não executa os processos digitados.**
A identificação de demonstração permanece no rodapé e no nome do resultado.
O Gantt começa no instante zero; o diagrama textual mostra a sequência completa.

## Estado da entrega

| Componente | Estado |
|---|---|
| Modelo de processo, leitores e diagrama textual | Já existiam; reutilizados |
| Interface Tkinter, importação, edição e validação | Implementados |
| Tabela comparativa, Gantt e controles de reprodução | Implementados |
| Round-Robin (`rr`) | Implementado e testado |
| Round-Robin com prioridade e envelhecimento (`rr_prio_aging`) | Implementado e testado |
| Motor, métricas e CLI do épico 1 | Dependência pendente |
| Algoritmos do épico 2 | Dependência pendente |

**Executar simulação** fica desabilitado enquanto `MotorSimulacao` não existir.
Os Round-Robin estão prontos para o motor; a GUI não contém um motor alternativo.
O comando geral `python -m src.scheduler` continua sendo responsabilidade da CLI do épico 1.

## Processos e configuração

Uma linha por processo, com chegada, duração e prioridade:

```text
0 5 2
0 2 3
1 4 1
3 3 4
```

IDs seguem a ordem da tabela. Chegada e prioridade devem ser inteiros não negativos;
duração, quantum e aging devem ser inteiros positivos.
Selecionar uma linha preenche o formulário; **Salvar edição** altera a linha,
enquanto **Adicionar** cria outra. Um arquivo inválido não apaga a tabela atual.

Configuração:

```text
quantum:2
aging:1
```

## Testes

```powershell
python -m unittest discover -s tests -v
```

Os testes de widgets precisam de sessão gráfica e Tkinter.
Para verificar apenas algoritmos e serviços, sem abrir janelas:

```powershell
python -m unittest discover -s tests -p test_round_robin.py -v
python -m unittest discover -s tests -p test_gui_services.py -v
```

## Integração e apresentação

Veja [o contrato e o roteiro do épico 3](docs/epico_3_interface.md).
As decisões anteriores e as novas convenções estão em
[decisões de implementação](docs/decisoes_implementacao.md).
