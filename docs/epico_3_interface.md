# Épico 3: interface, integração e apresentação

## Caminho dos dados

`EntradaWidget + ConfigWidget → ControladorGUI → ServicoReal → fábrica + motor → ResultadoGUI → widgets`

- Widgets coletam e exibem dados. Não simulam processos e não calculam métricas.
- O controlador reutiliza `ler_processos` e `ler_configuracao` e valida a seleção.
- `ServicoSimulacao` define `listar_algoritmos()` e `executar(processos, config, algoritmos)`.
- `ServicoReal` cria processos, configuração e escalonador novos para cada algoritmo.
- `ServicoDemonstrativo.carregar()` devolve uma fixture fixa, sem receber a entrada.
- A comparação aceita qualquer quantidade de algoritmos e possui rolagem.
- O motor roda numa thread de trabalho. Somente a thread principal acessa Tkinter,
  recebendo a resposta por fila e `after()`. Fechar a janela não aguarda o worker.
- A animação reproduz uma execução pronta; não modifica os processos.
  Pausar, reiniciar, trocar o resultado e fechar cancelam o callback pendente.

## Contrato para o épico 1

O motor compartilhado agora está implementado para permitir a execução real dos
processos cadastrados. Ele não contém condições específicas para Round-Robin:
trabalha somente com a interface base, que os demais algoritmos também usarão.
O adaptador mantém a importação adiada e a mensagem de indisponibilidade para
compatibilidade com versões do projeto em que o motor ainda não existe.

A forma esperada é uma classe sem argumentos de construção:

```python
class MotorSimulacao:
    def executar(self, processos, escalonador, config):
        # Retorna ResultadoSimulacao
        ...
```

O resultado deve expor:

| Campo | Tipo / significado |
|---|---|
| nome_algoritmo | str |
| tt_medio | float, média de término menos chegada |
| tw_medio | float, média de turnaround menos duração original |
| trocas_contexto | int |
| diagrama | str, diagrama textual já renderizado |
| registros | opcional: sequência de pares (executando, presentes) |
| esperas | sequência de pares (ID, espera total em segundos), na ordem da entrada |

Cada elemento de `registros` corresponde a um segundo, desde t=0, inclusive ócio.
`executando` é o ID de um processo ou `None`; `presentes` é uma coleção dos IDs
que já chegaram e ainda estavam ativos **no início daquele tick**.

Exemplo de resultado estruturado:

```python
registros = (
    ("P1", frozenset({"P1", "P2"})),
    ("P2", frozenset({"P2"})),
    (None, frozenset()),  # segundo ocioso também ocupa uma coluna
)
```

É possível adicionar esse campo ao resultado sem importar a GUI.
O adaptador faz a conversão para as dataclasses imutáveis `ResultadoGUI` e `TickGUI`.
Se `registros` não existir ou for `None`, a tabela e o texto continuam funcionando;
o Gantt informa a ausência dos registros e desabilita a reprodução.
Não há acesso à propriedade privada `DiagramaTempo._ticks`.
O motor pode manter um histórico público ou oferecer uma cópia pública do diagrama.

### Ordem das chamadas por tick

1. Entregar chegadas do instante t via `ao_chegar(processo, t)`.
2. Chamar `selecionar_proximo(t, atual)`.
3. Guardar o ID escolhido e os presentes para o diagrama desse segundo.
4. Executar uma unidade de CPU e atualizar as métricas e estados.
5. Chamar `ao_finalizar_tick(t, escolhido)`, **inclusive quando escolhido acabou de terminar**.
6. Avançar o relógio. Um processo encerrado pode ser passado à próxima seleção ou substituído por None.

Os Round-Robin usam `tempo_restante` para reconhecer conclusão; não dependem de
um novo hook. A interface base atual não tem `ao_finalizar_processo`; o motor usa somente
os três métodos existentes.

## Contrato para o épico 2

Os módulos conhecidos são importados pela fábrica antes de listar ou criar
escalonadores. Cada colega implementa sua classe e registra seu nome:

```python
registrar("fcfs", FCFS)
# Construtor: FCFS(configuracao, aleatorio)
```

Os módulos já existentes `fcfs`, `sjf`, `srtf` e `priority` estão incluídos
nesse carregamento. Usar os nomes previstos: `fcfs`, `sjf`, `srtf`, `prioc`, `priop`.
Se houver novo módulo, adicioná-lo ao carregamento da fábrica. Nenhuma tela
instancia algoritmos diretamente. Reiniciar a GUI após acrescentar um algoritmo.

## Convenções dos Round-Robin

### Round-Robin simples

Fila FIFO com `deque`. O processo continua até concluir ou consumir seu quantum.
Na seleção após o esgotamento, o processo inacabado retorna ao fim da fila.
Como o motor entrega chegadas antes da seleção, uma chegada na fronteira já está
na fila quando o processo anterior retorna. Ociosidade e término antecipado não
transferem o quantum consumido para o processo seguinte.

### Round-Robin com prioridade e envelhecimento

Maior valor significa maior prioridade. Não há preempção por prioridade no meio
da fatia. A escolha restaura a prioridade estática do processo selecionado.
Empates seguem a função compartilhada: processo atual, menor tempo restante,
sorteio. O serviço usa uma nova fonte `random.Random(0)` por execução para
facilitar a reprodução na apresentação.

Apenas ao fechar um quantum **completo**, incrementar a prioridade dinâmica dos
processos que estavam esperando. Quem executou não envelhece; uma chegada no
instante seguinte não recebe envelhecimento retroativo. Não envelhecer na
primeira seleção, durante ócio ou após fatia incompleta. Uma conclusão exatamente
no fim do quantum ainda fecha um quantum completo.

Essa é a interpretação adotada do PDF e substitui comentários que falavam em
aging por tick ou por toda seleção. Deve ser comunicada ao grupo para manter
uma semântica única. Usa lista de prontos, pois suas prioridades mudam; assim não
há necessidade de reconstruir um heap ou corrigir suas chaves a cada atualização.

## Demonstração e validação

A fixture usa os quatro processos do enunciado e uma sequência fixa de 14 segundos.
Ela tem tempo médio de vida 9,75, espera média 6,25 e 7 trocas. Esses números
descrevem apenas a fixture; não são as médias dos slides citadas nos stories.
Os dados dos slides não foram fornecidos e não são usados como oráculo de teste.

Os testes dos algoritmos usam um driver pequeno que faz as chamadas por tick e
confere sequências esperadas. Esse driver está apenas nos testes.
Os testes do serviço usam um motor falso para verificar cópias independentes,
adaptação de resultados e ausência de efeitos na entrada original.
Os testes de Tk verificam edição, preservação de dados inválidos, reprodução,
cancelamento e atualização da tela pelo serviço substituto.

## Roteiro de apresentação

1. Abrir com `python -m src.scheduler.gui` e identificar os quatro painéis.
2. Carregar o exemplo; selecionar uma linha, editar duração e salvar.
3. Tentar uma duração inválida e mostrar que a entrada válida é preservada.
4. Selecionar Round-Robin e clicar em **Executar simulação**.
5. Selecionar o resultado e mostrar espera individual, reprodução, pausa, avanço,
   **Ir ao fim** e troca de abas com **Ctrl+Tab**.
6. Explicar a fila do RR simples e o contador de quantum.
7. Explicar a prioridade dinâmica e o envelhecimento somente na fatia completa.
8. Mostrar um teste de chegada na fronteira e outro de envelhecimento.
9. Mostrar que a fábrica e o adaptador permitem integrar os demais algoritmos
   sem mudar os widgets.

Quando os demais algoritmos forem registrados, repetir o roteiro para comparar
suas execuções reais. O motor atual já utiliza o mesmo contrato.

## Explicação simples do Round-Robin e da espera

Imagine uma fila para usar a CPU. Quem está no início executa por no máximo
um quantum. Se acabar seu trabalho, sai; se ainda faltar trabalho, volta ao fim
da fila. O contador da fatia é zerado ao escolher o próximo processo.

Com quantum 2, P1 chegando em 0 e durando 3 segundos, e P2 chegando em 1 e
durando 1 segundo, a sequência é:

| Intervalo | CPU |
|---|---|
| 0–1 | P1 |
| 1–2 | P1 |
| 2–3 | P2 |
| 3–4 | P1 |

P1 termina em 4: espera = 4 − 0 − 3 = 1 segundo.
P2 termina em 3: espera = 3 − 1 − 1 = 1 segundo.
A média de espera é 1 segundo. O motor reúne as métricas e as fornece à GUI.
Só mudanças diretas entre processos diferentes contam como trocas de contexto;
entrar ou sair de um intervalo ocioso não incrementa o contador.

## Troca rápida de visualização

O texto é preenchido somente ao selecionar um resultado novo. O Canvas mantém
as células visíveis e atualiza apenas as que mudam com o avanço da reprodução.
Redimensionamentos são agrupados em uma atualização pendente; quando a aba
textual está aberta, o Canvas não redesenha. Ao voltar, ele mostra o instante
atual. Pausado ou finalizado, mudar de aba reaproveita o desenho existente.

O botão **Ir ao fim** mostra toda a execução sem aguardar a animação.
Os totais de espera são sempre da execução completa; não são contadores parciais
da reprodução. A execução real e a demonstração continuam explicitamente separadas.
