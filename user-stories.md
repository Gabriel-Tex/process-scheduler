# Planejamento do Simulador de Escalonamento de Processos

**Aviso: esse documento foi gerado por IA para fins de planejamento e organização do projeto. Ele não substitui a comunicação direta entre os membros da equipe, mas serve como referência para dividir tarefas e acompanhar o progresso.**

## 🎯 Estratégia de Divisão

Para os 3 épicos ficarem o mais independentes possível, a chave é isolar o que todo mundo depende (o "contrato") em histórias curtas e prioritárias dentro do **Épico 1**, e comunicá-las ao time assim que ficarem prontas — mesmo antes do Épico 1 terminar por completo. 

Especificamente: as duas primeiras histórias do Épico 1 (modelo de domínio + interface `EscalonadorBase`/fábrica) devem sair primeiro, porque são o que os Épicos 2 e 3 importam para trabalhar. A partir daí, os três épicos correm em paralelo sem se bloquear.

### Divisão por Responsável

* **Épico 1 — Núcleo, E/S e Motor de Simulação (+ CLI):** Trabalho de infraestrutura, sem "algoritmo" nenhum — é quem sustenta os outros dois.
* **Épico 2 — Algoritmos por Seleção:** FCFS, SJF, SRTF, Prioridade Cooperativa e Prioridade Preemptiva (5 algoritmos que compartilham a mesma "forma", então depois do primeiro os demais saem rápido).
* **Épico 3 — Algoritmos por Fila Circular + Interface Gráfica:** Os 2 algoritmos mais "mecânicos" (Round-Robin e Round-Robin com envelhecimento) para satisfazer quem quer mexer em algoritmo, e toda a GUI, que é o grosso do trabalho desse épico.

> **Equilíbrio de Carga:** ~7 a 10 histórias por pessoa, com naturezas diferentes mas esforço total comparável.

---

## 📌 Épico 1 — Núcleo do Domínio, E/S e Motor de Simulação
**Responsável:** Membro 1

### 1.1 Modelagem do domínio
* **História:** Como desenvolvedor, quero as entidades `Processo`, `StatusProcesso` e `Configuracao` prontas, para que os outros dois épicos tenham um contrato estável desde o primeiro dia.
* **Critérios de Aceitação:**
  * `Processo` guarda: id, instante de criação, tempo de processamento (duração original), tempo restante, prioridade estática, prioridade dinâmica, status, instante de início/término.
  * `Configuracao` guarda: `quantum` e `aging`.
* **Passos:**
  1. Criar `StatusProcesso` (enum: `NOVO`, `PRONTO`, `EXECUTANDO`, `FINALIZADO`).
  2. Criar `Processo` como dataclass com os campos acima, um método `executar_um_tick()` e uma property `finalizado`.
  3. Criar `Configuracao` como dataclass simples.
  4. ⚠️ **Avisar o time assim que este arquivo estiver pronto** — é o bloqueio principal dos outros épicos.
* **Arquivos:** `src/scheduler/domain/process.py`, `src/scheduler/domain/configuration.py`

### 1.2 Interface abstrata dos escalonadores + regra de desempate + fábrica
* **História:** Como desenvolvedor, quero uma interface comum (`EscalonadorBase`) e uma função de desempate compartilhada, para que qualquer algoritmo implementado pelos colegas se encaixe no motor sem alterações.
* **Critérios de Aceitação:**
  * Desempate segue exatamente a regra da tarefa:
    1. Processo já em execução;
    2. Menor tempo restante;
    3. Escolha aleatória.
  * Existe um registro (`factory.py`) que mapeia `nome do algoritmo → construtor`, vazio no início, para os colegas registrarem suas classes.
* **Passos:**
  1. Definir `EscalonadorBase` com `ao_chegar`, `selecionar_proximo` (abstrato) e `ao_finalizar_tick` (hook opcional, no-op por padrão).
  2. Implementar `desempatar(candidatos, em_execucao, aleatorio)` seguindo a regra dos 3 critérios.
  3. Receber um `random.Random` por injeção (não usar `random` global direto), para deixar comportamento reprodutível.
  4. Criar `factory.py` com `registrar(nome, construtor)`, `criar(nome, configuracao, aleatorio)` e `listar_algoritmos()`.
  5. ⚠️ **Publicar essa interface para o time** (ex.: num PR pequeno) antes de seguir para as próximas histórias.
* **Arquivos:** `src/scheduler/schedulers/base.py`, `src/scheduler/schedulers/factory.py`

### 1.3 Leitura da entrada padrão (stdin)
* **História:** Como usuário do simulador, quero fornecer processos via `stdin` no formato `instante duração prioridade`, para simular meu próprio cenário.
* **Critérios de Aceitação:**
  * Cada linha vira um processo, com id atribuído na ordem em que aparece (`P1`, `P2`, ...), não reordenado por instante de chegada.
  * Erros de formato geram `EntradaInvalidaError` (subclasse de `ValueError`) com indicação do número da linha.
* **Passos:**
  1. Implementar `ler_processos(entrada: TextIO) -> list[Processo]` — recebe o fluxo de texto por parâmetro, sem chamar `sys.stdin` diretamente (desacoplamento da fonte concreta).
  2. Fazer split por espaços (um ou mais) e converter para inteiros.
  3. Não duplicar a validação de domínio (`tempo_processamento > 0`, `instante_criacao >= 0`, `prioridade_estatica >= 0`) — propagar o `ValueError` do `Processo.__post_init__` com contexto de linha.
  4. Ignorar linhas em branco silenciosamente.
  5. Retornar lista de `Processo` na ordem de leitura.
* **Arquivos:** `src/scheduler/io/input_reader.py`

### 1.4 Leitura do arquivo de configuração
* **História:** Como usuário do simulador, quero configurar quantum e taxa de envelhecimento por um arquivo texto, para parametrizar os algoritmos Round-Robin.
* **Critérios de Aceitação:**
  * Aceita o formato `quantum:2` / `aging:1` exatamente como no exemplo da tarefa.
  * Ambas as chaves são obrigatórias; ausência de qualquer uma levanta `ConfiguracaoInvalidaError`.
  * Chaves desconhecidas e chaves repetidas são tratadas como erro.
* **Passos:**
  1. Implementar `ler_configuracao(arquivo: TextIO) -> Configuracao` — recebe o arquivo já aberto por parâmetro, sem chamar `open()` internamente.
  2. Dividir cada linha por `:` (com `maxsplit=1`), tolerar espaços em branco extras e normalizar chaves para minúsculas.
  3. Validar que `quantum > 0` e `aging > 0` (a `Configuracao` não possui validação interna).
  4. Ignorar linhas em branco e linhas de comentário (iniciadas por `#`).
  5. Montar e retornar um `Configuracao`.
* **Arquivos:** `src/scheduler/io/config_reader.py`

### 1.5 Diagrama de tempo
* **História:** Como usuário do simulador, quero ver o diagrama de execução tick a tick, para visualizar como cada algoritmo se comportou.
* **Critérios de Aceitação:**
  * Uma linha por segundo:
    * `##` para quem está executando;
    * `--` para quem está pronto/aguardando;
    * Célula em branco para quem ainda não chegou ou já terminou.
  * Formato idêntico ao exemplo do enunciado.
  * Funciona com zero ticks (devolve apenas o cabeçalho).
* **Passos:**
  1. Criar `DiagramaTempo(ids_processos: Sequence[str])` — fixa a ordem das colunas na criação, independente do domínio (trabalha só com `str` e conjuntos).
  2. Implementar `registrar_tick(executando: str | None, presentes: Iterable[str])` — tempo implícito pela ordem das chamadas (tick 0, 1, 2, …).
  3. Implementar `renderizar() -> str` — devolve o diagrama formatado como texto, sem chamar `print`.
  4. Colunas de largura dinâmica, alinhadas à direita, separadas por dois espaços.
* **Arquivos:** `src/scheduler/simulator/diagram.py`

### 1.6 Cálculo de métricas e resultado consolidado
* **História:** Como usuário do simulador, quero ver tempo médio de execução, tempo médio de espera e número de trocas de contexto por algoritmo, para comparar os algoritmos entre si.
* **Critérios de Aceitação:**
  * `tt` e `tw` calculados como média sobre todos os processos (validados apenas para finalizados).
  * Trocas de contexto contam apenas transições consecutivas diretas entre processos diferentes.
* **Passos:**
  1. Implementar `calcular_tempos_medios(processos)` para derivar o turnaround (`término − criação`) e espera (`turnaround − duração`) de cada finalizado e retornar as médias.
  2. Implementar `contar_trocas_contexto(execucoes)` validando transições diretas.
  3. Montar a `ResultadoSimulacao` imutável (`@dataclass(frozen=True)`) com o nome do algoritmo, médias, trocas e diagrama.
  4. Implementar `construir_resultado(...)` para facilitar a instanciação da dataclass.
* **Arquivos:** `src/scheduler/simulator/result.py`

### 1.7 Motor de simulação
* **História:** Como desenvolvedor, quero um motor único que receba uma lista de processos e um `EscalonadorBase` e devolva um `ResultadoSimulacao`, para reaproveitar a mesma lógica em todos os 7 algoritmos.
* **Critérios de Aceitação:**
  * Funciona de forma idêntica para algoritmos cooperativos e preemptivos, sem `if` especial por algoritmo dentro do motor.
* **Passos:**
  1. Implementar laço por tick:
     1. Processar chegadas do instante atual;
     2. Chamar `selecionar_proximo`;
     3. Contar troca de contexto se mudou;
     4. Executar 1 segundo do processo escolhido;
     5. Marcar finalização se zerou o tempo restante;
     6. Chamar `ao_finalizar_tick`;
     7. Registrar linha no diagrama.
  2. Parar quando todos os processos estiverem finalizados.
  3. Garantir que cada chamada ao motor recebe/gera cópias novas de `Processo` (nunca reaproveitar instâncias entre execuções).

### 1.8 Escrita da saída formatada
* **História:** Como usuário do simulador, quero a saída impressa no terminal exatamente no formato pedido pela atividade, para poder entregar a saída do programa.
* **Passos:**
  1. Receber um ou mais `ResultadoSimulacao` e formatar `tt`, `tw`, trocas de contexto e diagrama como texto.
  2. Manter essa formatação isolada da lógica de cálculo (o motor não sabe imprimir nada).

### 1.9 CLI orquestradora
* **História:** Como usuário do simulador, quero rodar `python -m escalonador --config config.txt < entrada.txt` e ver o resultado de todos os algoritmos (ou de um específico), para usar o simulador via linha de comando.
* **Critérios de Aceitação:**
  * Por padrão, roda os 7 algoritmos sobre o mesmo conjunto de processos e imprime um bloco por algoritmo, ao final com uma tabela comparativa (como o "Quadro Comparativo" dos slides).
  * Aceita flag para rodar só um algoritmo específico.
* **Passos:**
  1. Usar `argparse` para `--config` e `--algoritmo` (opcional).
  2. Ler `stdin` e `config`.
  3. Para cada algoritmo registrado na fábrica: criar instância nova, criar processos novos, rodar o motor, guardar resultado.
  4. Imprimir tudo via `escritor_saida`, terminando com a tabela comparativa.

### 1.10 Consolidação do documento de decisões de implementação (colaborativa)
* **História:** Como equipe, queremos um documento único descrevendo as decisões de implementação, estruturas de dados e padrões de projeto usados, para atender à exigência da atividade.
* **Passos:**
  1. Membro 1 escreve a seção de arquitetura geral, domínio, E/S e motor.
  2. Membro 2 e Membro 3 completam a seção do seu próprio épico (algoritmos e GUI) — combinar um prazo comum próximo à entrega final.
  3. Membro 1 consolida tudo em `docs/decisoes_implementacao.md`.

---

## 📌 Épico 2 — Algoritmos por Seleção
**Responsável:** Membro 2  
*(Depende apenas das histórias 1.1 e 1.2 do Épico 1)*

### 2.1 FCFS (First-Come, First-Served)
* **História:** Como usuário do simulador, quero escalonar processos pela ordem de chegada, para ter a linha de base de comparação entre os algoritmos.
* **Passos:**
  1. Implementar `FCFS(EscalonadorBase)`: manter lista de prontos; `selecionar_proximo` devolve quem já está executando (não interrompe); se CPU ociosa, escolhe o de menor instante de criação usando desempate.
  2. Registrar `"fcfs"` na fábrica.
  3. Validar manualmente com o dataset dos slides (T1–T5): deve dar `tt=8,0` / `tw=5,2` / `4` trocas de contexto.

### 2.2 Extrair a base comum de "seleção por chave"
* **História:** Como desenvolvedor, quero abstrair a lógica comum entre FCFS, SJF e Prioridade Cooperativa em uma classe base reaproveitável, para não duplicar código nas próximas histórias.
* **Passos:**
  1. Criar uma classe intermediária parametrizada por `chave` (função) e `preemptivo` (bool).
  2. Reescrever o FCFS de 2.1 como uma instância dessa classe (`chave = instante de criação`, `preemptivo = False`).
  3. Confirmar que o teste manual de 2.1 continua batendo.

### 2.3 SJF (Shortest Job First)
* **História:** Como usuário do simulador, quero escalonar pela menor duração total, para reduzir o tempo médio de espera.
* **Passos:**
  1. Instanciar a base de 2.2 com `chave = duração original`, `preemptivo = False`.
  2. Registrar `"sjf"` na fábrica.
  3. Validar com o dataset dos slides: `tt=5,8` / `tw=3,0` / `4` trocas.

### 2.4 Prioridade Cooperativa (PRIOc)
* **História:** Como usuário do simulador, quero escalonar por prioridade estática sem preempção, para simular ambientes onde trocar de contexto é caro mas a prioridade ainda importa.
* **Passos:**
  1. Confirmar com o time a convenção de prioridade (maior valor = mais prioridade, como nos slides) — deixar documentado.
  2. Instanciar a base de 2.2 com `chave = prioridade (decrescente)`, `preemptivo = False`.
  3. Registrar `"prioc"` na fábrica.
  4. Validar: `tt=6,6` / `tw=3,8` / `4` trocas.

### 2.5 SRTF (Shortest Remaining Time First)
* **História:** Como usuário do simulador, quero a versão preemptiva do SJF, para minimizar ainda mais o tempo de espera.
* **Passos:**
  1. Instanciar a base de 2.2 com `chave = tempo restante`, `preemptivo = True` (incluir o processo em execução no conjunto de candidatos a cada tick).
  2. Registrar `"srtf"` na fábrica.
  3. Validar: `tt=5,4` / `tw=2,6` / `5` trocas.

### 2.6 Prioridade Preemptiva (PRIOp)
* **História:** Como usuário do simulador, quero escalonar por prioridade com preempção, para que tarefas mais importantes tomem a CPU assim que chegam.
* **Passos:**
  1. Instanciar a base de 2.2 com `chave = prioridade`, `preemptivo = True`.
  2. Registrar `"priop"` na fábrica.
  3. Validar: `tt=5,6` / `tw=2,8` / `6` trocas.

### 2.7 Fechamento do épico
* **História:** Como equipe, queremos garantir que os 5 algoritmos estão registrados e corretos antes da integração final.
* **Passos:**
  1. Conferir que os 5 nomes estão na fábrica.
  2. Rodar manualmente (assim que a CLI do Épico 1 estiver pronta) com o dataset dos slides e comparar todos os números com o "Quadro Comparativo".
  3. Escrever a seção correspondente no documento de decisões (história 1.10).

---

## 📌 Épico 3 — Algoritmos por Fila Circular + Interface Gráfica
**Responsável:** Membro 3  
*(As histórias 3.1–3.2 dependem de 1.1/1.2; a GUI depende de 1.6/1.7/1.9 — mas 3.3 já pode iniciar em paralelo com mocks)*

### 3.1 Round-Robin puro
* **História:** Como usuário do simulador, quero escalonar por revezamento de tempo com quantum fixo, para obter mais justiça na distribuição da CPU.
* **Passos:**
  1. Implementar `RoundRobin(EscalonadorBase)` com uma fila (`collections.deque`).
  2. `ao_chegar`: adiciona ao fim da fila. 
  3. `selecionar_proximo`: se CPU ociosa, tira do início da fila; se quantum do processo atual esgotou, devolve-o ao fim da fila e tira o próximo.
  4. Usar `ao_finalizar_tick` para contar o quantum consumido.
  5. Registrar `"rr"` na fábrica.
  6. Validar com `quantum=2` no dataset dos slides: `tt=8,4` / `tw=5,6` / `7` trocas.

### 3.2 Round-Robin com prioridade e envelhecimento
* **História:** Como usuário do simulador, quero um Round-Robin cuja escolha do próximo processo, a cada quantum, considere a prioridade dinâmica com envelhecimento, para equilibrar justiça e importância.
* **Critérios de Aceitação:**
  * Envelhecimento ocorre a cada quantum (não a cada tick).
  * Sem preempção por prioridade no meio do quantum (regra explícita da tarefa).
* **Passos:**
  1. Manter um conjunto de prontos, cada um com prioridade dinâmica (inicia igual à estática).
  2. Ao fim de cada quantum (ou quando a CPU fica ociosa): escolher quem tem maior prioridade dinâmica (usando desempate em caso de empate); quem foi escolhido volta à prioridade estática; todos os demais ganham `+aging`.
  3. Novo processo que chega entra com `prioridade dinâmica = estática`, sem interromper quem está rodando.
  4. Registrar `"rr_prio_aging"` na fábrica.
  5. Validar aproximadamente contra o slide do PRIOd (ciente de que os números batem exatamente só com `quantum=1`, já que o slide não usa fatias maiores).

### 3.3 Esqueleto da aplicação gráfica
* **História:** Como usuário do simulador, quero abrir uma janela com painéis para entrada, configuração, resultados e diagrama, para não depender da linha de comando.
* **Passos:**
  1. Escolher o framework (`Tkinter + ttk` como opção padrão sem dependências externas).
  2. Criar a janela principal com placeholders para os 4 painéis (entrada, config, resultado, gantt) e um botão "Executar".
  3. Ligar o botão a uma chamada mockada para validar o fluxo em paralelo ao Épico 1.

### 3.4 Widget de entrada de processos e configuração
* **História:** Como usuário do simulador, quero inserir/editar/remover processos e definir quantum/aging pela interface, para montar cenários sem editar arquivos manualmente.
* **Passos:**
  1. Criar uma tabela editável (`ttk.Treeview` ou grade de `Entry`) com colunas instante/duração/prioridade e botões de adicionar/remover linha.
  2. Criar campos numéricos para `quantum` e `aging`.
  3. Adicionar validação simples (mesmas regras da história 1.3) com mensagens de erro visuais.
  4. *(Opcional)* Botão "Carregar de arquivo" reaproveitando os leitores do Épico 1.

### 3.5 Controlador — ligação da GUI com o núcleo
* **História:** Como usuário do simulador, quero clicar em "Executar" e ver os resultados de todos os algoritmos, para comparar rapidamente sem usar a CLI.
* **Passos:**
  1. Criar `controlador.py`: lê os dados dos widgets, monta `Configuracao` e lista de processos.
  2. Percorrer os algoritmos registrados na fábrica rodando o motor para cada um.
  3. Guardar a lista de `ResultadoSimulacao` para os widgets de exibição consumirem.
  4. ⚠️ **Importante:** A GUI nunca deve instanciar algoritmos diretamente — sempre via fábrica, evitando acoplamento.

### 3.6 Widget de resultados
* **História:** Como usuário do simulador, quero ver tt, tw e trocas de contexto de cada algoritmo lado a lado, para comparar como no quadro comparativo do professor.
* **Passos:**
  1. Criar uma aba ou tabela por algoritmo com as métricas consolidadas.
  2. Montar uma tabela-resumo final no estilo do "Quadro Comparativo" dos slides.

### 3.7 Gantt animado (Bônus)
* **História:** Como usuário do simulador, quero ver um diagrama de Gantt animado avançando tick a tick, para visualizar a execução de forma intuitiva.
* **Passos:**
  1. Criar um `Canvas` desenhando uma barra colorida por processo.
  2. Usar `widget.after(ms, callback)` para avançar um tick por vez, lendo os dados do `DiagramaTempo`.
  3. Adicionar controles de play/pause/velocidade, se o tempo permitir.

## Nota de revisão da implementação

Este arquivo preserva o planejamento original. A convenção implementada de
aging é detalhada em `docs/epico_3_interface.md`: somente processos em espera
recebem incremento ao completar um quantum; não há incremento no ócio, na
primeira seleção ou após término antecipado. Isso corrige a divergência com
o passo 3.2 que menciona incremento por seleção/ociosidade.
As médias dos slides acima não são oráculos verificados sem suas entradas.
Veja `docs/revisao_projeto.md` para requisitos explícitos e ambiguidades do PDF.
