# Simulador de Escalonamento de Processos

Projeto da disciplina de Sistemas Operacionais, em Python.

## Rodar depois de clonar

Com Python 3.10 ou superior e Tkinter instalados, abra um terminal na raiz do
repositório e execute:

```text
python SimuladorEscalonamento.pyz
```

O arquivo portátil está incluído na raiz; não precisa gerar executável nem
instalar dependências com pip. No Linux/macOS, o comando pode ser `python3`.
Tkinter e uma sessão gráfica são necessários.

O `.pyz` é uma versão empacotada do código. Durante o desenvolvimento, use o
comando abaixo para executar imediatamente suas alterações nos arquivos `src/`.

## Abrir a interface pelo código

Na raiz do repositório, em um terminal com Python **3.10 ou superior** e Tkinter:

```powershell
python -m src.scheduler.gui
```

Se o Windows disponibilizar Python pelo launcher, use `py -m src.scheduler.gui`.
Para verificar Tkinter: `python -m tkinter` deve abrir uma pequena janela de teste.
Não há dependências externas para a interface ou os testes.

1. Clique em **Carregar exemplo** ou cadastre os processos.
2. Ajuste quantum e aging, ou carregue o arquivo `config/config.txt`.
3. Selecione **Round-Robin** e/ou **Round-Robin + envelhecimento**.
4. Clique em **Executar simulação** para usar os processos cadastrados.
5. Selecione um resultado; clique em **Reproduzir**, **Avançar** ou **Ir ao fim**.

O painel **Espera por processo** mostra o tempo total que cada processo esperou
na execução selecionada, em segundos. São valores da execução completa,
independentes do ponto da reprodução: término − chegada − duração.
**Ctrl+Tab** alterna Gantt e texto sem reiniciar a reprodução.
Para modificar uma linha existente, use **Editar** antes de executar.

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
| Motor simples e métricas (incluindo espera individual) | Implementados para habilitar a execução real |
| CLI do épico 1 | Dependência pendente |
| Algoritmos do épico 2 | Dependência pendente |

**Executar simulação** está habilitado: um único motor compartilhado executa
os dois Round-Robin e pode receber os algoritmos dos colegas.
O botão **Ver demonstração** continua separado, apenas como exemplo visual.
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
Selecionar uma linha preenche o formulário; **Editar** altera a linha,
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
python -m unittest discover -s tests -p test_engine.py -v
python -m unittest discover -s tests -p test_gui_services.py -v
```

## Integração e apresentação

Veja [o contrato e o roteiro do épico 3](docs/epico_3_interface.md).
As decisões anteriores e as novas convenções estão em
[decisões de implementação](docs/decisoes_implementacao.md).

## Preempção e navegação

**Permitir preempção** é um filtro dos algoritmos oficiais, inicialmente marcado:

- Marcado: permite escolher também RR, RR com envelhecimento, SRTF e Prioridade Preemptiva.
- Desmarcado: mantém apenas FCFS, SJF e Prioridade Cooperativa, quando registrados.
- Nos Round-Robin, a preempção ocorre por quantum; nunca por chegada de prioridade maior.
- Prioridade Preemptiva e SRTF seguem suas próprias regras quando forem implementados.

Quantum só fica editável para Round-Robin; aging só para RR com envelhecimento.
A opção não converte RR em outro algoritmo. Enquanto o épico 2 estiver pendente,
desmarcar a opção deixa a lista sem algoritmos e a tela explica o motivo.

**Voltar** pausa e recua um segundo, sem alterar a execução calculada.
A aba selecionada fica cinza, com fonte maior e em negrito. Use **Editar**
para aplicar alterações na linha selecionada.

### Por que quantum zero não é aceito?

A história 1.4 do planejamento exige `quantum > 0`. As histórias 3.1 e 3.2
usam uma fatia de tempo positiva para o Round-Robin e seu envelhecimento.
Interpretar zero como uma fatia ilimitada mudaria essas políticas. Portanto,
zero continua inválido; algoritmos sem quantum deixam esse campo desabilitado.
O arquivo de configuração mantém o contrato original de valores positivos.
