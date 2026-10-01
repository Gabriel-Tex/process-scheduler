# Simulador de Escalonamento de Processos: Histórias de Usuário 

**Aviso: esse documento foi gerado por IA para fins de planejamento e organização do projeto. Ele não substitui a comunicação direta entre os membros da equipe, mas serve como referência para dividir tarefas e acompanhar o progresso.**

## Regras do enunciado que valem para todas as histórias

1. Linguagem: Python.
2. Entrada: processos lidos da **entrada padrão (stdin)**, uma linha por processo, com três inteiros separados por **um ou mais espaços em branco**: instante de criação, duração em segundos e prioridade estática (escala positiva). A listagem **não precisa estar ordenada** por instante de criação.
3. Configuração: arquivo de texto plano com `quantum:2` e `aging:1`.
4. Saída padrão (stdout), **para cada algoritmo**: tempo médio de vida (tt), tempo médio de espera (tw), número de trocas de contexto e diagrama de tempo (uma linha por segundo, na vertical).
5. **Desempate** na escolha do processo que ocupa o processador: (i) o processo que já está com o processador; (ii) o de menor tempo restante; (iii) escolha aleatória.
6. Round-Robin com prioridade e envelhecimento: o envelhecimento ocorre **a cada quantum** e **não há preempção por prioridade**.
7. Entregáveis: código **devidamente comentado** e documento de decisões de implementação (classes, estruturas de dados, padrões de projeto, estrutura do processo com id, status, prioridade).
8. Interface visual: bônus, a critério da equipe.

### Definição de pronto (vale para toda história)

- Código comentado (docstrings e comentários nos pontos não óbvios).
- Testes automatizados ou validação manual registrada.
- Nenhuma dependência de `sys.stdin`/`open()` dentro da lógica de domínio (a E/S fica nas bordas).

## Estratégia de divisão

As histórias 1.1 e 1.2 formam o contrato e devem ser publicadas primeiro. A partir delas, os três épicos correm em paralelo.

- **Épico 1** — Núcleo, E/S, motor de simulação e CLI (Membro 1).
- **Épico 2** — Algoritmos por seleção: FCFS, SJF, SRTF, PRIOc, PRIOp (Membro 2).
- **Épico 3** — Round-Robin, Round-Robin com envelhecimento e interface gráfica (Membro 3).

---

## Épico 1: Núcleo do Domínio, E/S e Motor de Simulação

### 1.1 Modelagem do domínio
- **História:** Como desenvolvedor, quero as entidades `Processo`, `StatusProcesso` e `Configuracao` prontas, para que os outros épicos tenham um contrato estável.
- **Critérios de aceitação:**
  - `Processo` guarda: id, instante de criação, duração original, tempo restante, prioridade estática, prioridade dinâmica, status, instante de início da primeira execução e instante de término.
  - `StatusProcesso`: `NOVO`, `PRONTO`, `EXECUTANDO`, `FINALIZADO`.
  - `Configuracao` guarda `quantum` e `aging` (ambos opcionais, `None` se ausentes).
  - Validação de domínio em `Processo.__post_init__`: duração > 0, instante de criação >= 0, prioridade >= 0.
  - Campos e métodos comentados (a estrutura do processo deve ser descrita no documento de decisões).
- **Arquivos:** `src/scheduler/domain/process.py`, `src/scheduler/domain/configuration.py`
- ⚠️ Avisar o time assim que estiver pronto.

### 1.2 Interface dos escalonadores, desempate e fábrica
- **História:** Como desenvolvedor, quero uma interface comum e uma função de desempate compartilhada, para que qualquer algoritmo se encaixe no motor sem alterações.
- **Critérios de aceitação:**
  - `EscalonadorBase` com `ao_chegar`, `selecionar_proximo` (abstrato) e `ao_finalizar_tick` (hook, no-op por padrão).
  - `desempatar(candidatos, em_execucao, aleatorio)` aplica **exatamente** a regra do enunciado: (i) processo em execução; (ii) menor tempo restante; (iii) escolha aleatória.
  - O desempate é aplicado **sempre que houver empate na chave principal do algoritmo**, inclusive no FCFS.
  - `random.Random` é injetado (comportamento reprodutível com semente).
  - `factory.py` com `registrar`, `criar` e `listar_algoritmos`.
- **Arquivos:** `src/scheduler/schedulers/base.py`, `src/scheduler/schedulers/factory.py`

### 1.3 🔧 Leitura da entrada padrão
- **História:** Como usuário, quero fornecer processos via stdin, no formato `instante duração prioridade`, para simular meu cenário.
- **Critérios de aceitação:**
  - Cada linha vira um processo, com id `P1`, `P2`, ... na **ordem de leitura** (sem reordenar por instante).
  - Campos separados por **um ou mais espaços em branco** (usar `split()` sem argumento, que também cobre tabs).
  - Linhas em branco são ignoradas.
  - Linha com número de campos diferente de 3 ou valor não inteiro gera `EntradaInvalidaError` (subclasse de `ValueError`) com o número da linha.
  - Erros de domínio (`ValueError` do `Processo`) são repassados com o número da linha, sem duplicar a validação.
  - Entrada sem nenhum processo gera erro claro.
- **Assinatura:** `ler_processos(entrada: TextIO) -> list[Processo]`
- **Arquivo:** `src/scheduler/io/input_reader.py`

### 1.4 🔧 Leitura do arquivo de configuração
- **História:** Como usuário, quero configurar quantum e taxa de envelhecimento por arquivo de texto plano, para parametrizar os algoritmos Round-Robin.
- **Critérios de aceitação:**
  - Aceita o formato `quantum:2` / `aging:1`, tolerando espaços extras e chaves em qualquer caixa.
  - Linhas em branco e comentários (`#`) são ignorados.
  - Valores devem ser inteiros > 0; caso contrário, `ConfiguracaoInvalidaError` com o número da linha.
  - Chave repetida ou desconhecida gera erro.
  - **Chave ausente não é erro na leitura:** o campo fica `None`. A obrigatoriedade é checada na criação do algoritmo (RR exige `quantum`; RR com envelhecimento exige `quantum` e `aging`; os demais não exigem nada). Assim, os cinco algoritmos sem quantum rodam mesmo sem configuração completa.
- **Assinatura:** `ler_configuracao(arquivo: TextIO) -> Configuracao`
- **Arquivo:** `src/scheduler/io/config_reader.py`

### 1.5 🔧 Diagrama de tempo
- **História:** Como usuário, quero ver o diagrama de execução, uma linha por segundo, para visualizar o comportamento de cada algoritmo.
- **Critérios de aceitação:**
  - Formato do enunciado: cabeçalho `tempo P1 P2 ...` e linhas `0- 1`, `1- 2`, ..., `10-11`.
  - Célula `##` para o processo executando, `--` para o processo presente e aguardando, e **em branco** para quem ainda não chegou ou já terminou.
  - Um processo conta como presente **desde o início do tick em que chega** (no exemplo do enunciado, P4, criado em 3, aparece como `--` na linha `3- 4`).
  - Tick ocioso (ninguém presente ou ninguém executando) gera linha só com o intervalo e células em branco.
  - Zero ticks devolve apenas o cabeçalho.
  - Colunas de largura dinâmica, alinhadas conforme o exemplo do enunciado.
  - **Teste de aceitação:** reproduzir exatamente o diagrama do enunciado (veja o oráculo na história 3.1).
- **API:** `DiagramaTempo(ids)`, `registrar_tick(executando, presentes)`, `renderizar() -> str` (sem `print`).
- **Arquivo:** `src/scheduler/simulator/diagram.py`

### 1.6 🔧 Métricas e resultado consolidado
- **História:** Como usuário, quero ver tt, tw, tempo de resposta e trocas de contexto por algoritmo, para compará-los.
- **Critérios de aceitação:**
  - `tt = média(término − criação)`.
  - `tw = média(tt do processo − duração)`.
  - **Tempo de resposta (tr)** `= média(instante da primeira execução − criação)`. Os objetivos da atividade citam essa métrica, embora a lista de saída não a exija; exibi-la é opcional e não substitui tt/tw.
  - **Trocas de contexto:** conta-se quando dois ticks consecutivos executam processos **diferentes** (`A` seguido de `B`). A primeira execução e tick ocioso entre processos **não** contam como troca. Esta convenção é registrada no documento de decisões.
  - `ResultadoSimulacao` imutável (`@dataclass(frozen=True)`) com nome do algoritmo, tt, tw, tr, trocas, tempo total e diagrama.
- **Arquivo:** `src/scheduler/simulator/result.py`

### 1.7 🔧 Motor de simulação
- **História:** Como desenvolvedor, quero um motor único que receba processos e um `EscalonadorBase` e devolva um `ResultadoSimulacao`, para reutilizar a lógica nos 7 algoritmos.
- **Critérios de aceitação:**
  - Sem `if` por algoritmo dentro do motor (cooperativo e preemptivo se comportam via `selecionar_proximo`).
  - Ordem dentro de cada tick: (1) registrar chegadas do instante atual (processos com mesmo instante entram na ordem de leitura); (2) `selecionar_proximo`; (3) contar troca de contexto se mudou; (4) executar 1 segundo; (5) marcar término se o tempo restante zerou; (6) `ao_finalizar_tick`; (7) registrar a linha no diagrama.
  - **Ticks ociosos:** se não há processo pronto, o tempo avança, a CPU fica ociosa e a linha é registrada em branco.
  - Termina quando todos os processos estiverem finalizados.
  - Cada execução usa **cópias novas** dos `Processo`.
  - Aceita entrada desordenada por instante de criação.
- **Arquivo:** `src/scheduler/simulator/engine.py`

### 1.8 🔧 Escrita da saída formatada
- **História:** Como usuário, quero a saída no stdout no formato pedido pela atividade, para poder entregá-la.
- **Critérios de aceitação:**
  - Para **cada algoritmo**, imprimir: nome, tt, tw, número de trocas de contexto e o diagrama de tempo.
  - Números médios com uma casa decimal e vírgula ou ponto de forma consistente (decisão documentada).
  - Formatação isolada da lógica de cálculo (o motor não imprime).
  - Função recebe `ResultadoSimulacao` e um `TextIO` de saída (testável).
- **Arquivo:** `src/scheduler/io/output_writer.py`

### 1.9 🔧 CLI orquestradora
- **História:** Como usuário, quero rodar `python -m scheduler [--config config.txt] [--algoritmo nome] < entrada.txt`, para usar o simulador pela linha de comando.
- **Critérios de aceitação:**
  - Lê processos do **stdin** e a configuração do arquivo indicado em `--config`. Sem a flag, tenta `config.txt` no diretório atual (o enunciado não define como o arquivo é passado, então o programa não pode quebrar quando o professor não passar argumentos). Se o arquivo não existir, algoritmos que não usam quantum/aging rodam normalmente e os demais informam o erro de forma clara.
  - Por padrão executa os 7 algoritmos sobre os mesmos processos e imprime um bloco por algoritmo.
  - Ao final, imprime uma tabela comparativa (tt, tw, trocas; tempo total opcional).
  - `--algoritmo` executa apenas um algoritmo (nomes validados contra a fábrica).
  - `--semente` (opcional) fixa o gerador aleatório do desempate.
  - Mensagens de erro de entrada vão para stderr, com código de saída diferente de zero.
- **Arquivos:** `src/scheduler/__main__.py`, `src/scheduler/cli.py`

### 1.10 🔧 Documento de decisões de implementação
- **História:** Como equipe, queremos o documento exigido pelo enunciado, para justificar nossas escolhas.
- **Critérios de aceitação:** `docs/decisoes_implementacao.md` contém:
  - classes e responsabilidades;
  - **estrutura do processo** (id, status, prioridade etc.);
  - estruturas de dados usadas (por exemplo `deque`, listas de prontos);
  - padrões de projeto (Strategy para os escalonadores, Factory/registro, separação E/S × domínio);
  - convenções adotadas onde o enunciado é omisso: prioridade (maior valor = maior prioridade), ordem na fila do RR, trocas de contexto, ticks ociosos, regra de aging, tratamento do empate no FCFS.
- **Passos:** Membro 1 escreve arquitetura, domínio, E/S e motor; Membros 2 e 3 escrevem as seções dos seus épicos; Membro 1 consolida.

---

## Épico 2: Algoritmos por Seleção
Depende apenas de 1.1 e 1.2.

### 2.1 🔧 FCFS
- **História:** Como usuário, quero escalonar pela ordem de chegada, para ter a linha de base de comparação.
- **Critérios de aceitação:**
  - Não preemptivo: o processo em execução segue até terminar.
  - Chave principal: instante de criação. Empates na chave são resolvidos pela regra do enunciado ((i) em execução; (ii) menor tempo restante; (iii) aleatório).
  - Registrado como `"fcfs"`.
- **Validação:**
  - Dataset dos slides (T1–T5): com o desempate do enunciado, T2 (duração 2) precede T1 (duração 5) em t=0. Resultado esperado: `tt=7,4`, `tw=4,6`, 4 trocas.
  - Os slides mostram `tt=8,0` / `tw=5,2`, porque rodam T1 antes de T2 (ordem de id). Essa divergência é esperada e deve ser registrada no documento de decisões. Para reproduzir os slides, basta remover o critério (ii) do FCFS.

### 2.2 Base comum de "seleção por chave"
- **História:** Como desenvolvedor, quero uma classe base parametrizada por `chave` e `preemptivo`, para não duplicar código entre FCFS, SJF, SRTF, PRIOc e PRIOp.
- **Critérios de aceitação:**
  - Em modo preemptivo, o processo em execução entra no conjunto de candidatos a cada tick.
  - Empates na chave sempre passam por `desempatar`.
  - Testes de 2.1 continuam passando após a refatoração.

### 2.3 SJF
- **Critérios de aceitação:** chave = duração original, não preemptivo, registrado como `"sjf"`.
- **Validação (slides):** `tt=5,8` / `tw=3,0` / 4 trocas.

### 2.4 🔧 Prioridade cooperativa (PRIOc)
- **Critérios de aceitação:**
  - Convenção **maior valor = maior prioridade** (enunciado diz apenas "escala de prioridades positiva", e a convenção vem dos slides). Documentada no documento de decisões.
  - Chave = prioridade estática (decrescente), não preemptivo, registrado como `"prioc"`.
- **Validação (slides):** `tt=6,6` / `tw=3,8` / 4 trocas.

### 2.5 SRTF
- **Critérios de aceitação:** chave = tempo restante, preemptivo, registrado como `"srtf"`. No empate com o processo em execução, ele permanece (regra (i)).
- **Validação (slides):** `tt=5,4` / `tw=2,6` / 5 trocas.

### 2.6 Prioridade preemptiva (PRIOp)
- **Critérios de aceitação:** chave = prioridade estática (decrescente), preemptivo, registrado como `"priop"`.
- **Validação (slides):** `tt=5,6` / `tw=2,8` / 6 trocas.

### 2.7 Fechamento do épico
- Os 5 nomes estão na fábrica.
- Comparar com o "Quadro Comparativo" dos slides, lembrando que o FCFS difere por causa do desempate (ver 2.1).
- Escrever a seção do épico no documento de decisões (1.10).

---

## Épico 3: Round-Robin e Interface Gráfica

### 3.1 🔧 Round-Robin (sem prioridade)
- **História:** Como usuário, quero revezamento por quantum fixo, sem considerar prioridade.
- **Critérios de aceitação:**
  - Usa `quantum` da configuração; erro claro se ausente.
  - Fila FIFO (`collections.deque`).
  - **Convenção da fila:** quando uma chegada e o fim de quantum ocorrem no mesmo instante, o processo recém-chegado entra na fila **antes** do processo preemptado (convenção observada nos slides 107, onde T3 chega em t=1, T1 volta em t=2 e a fila fica T3 à frente de T1).
  - Um processo que termina antes do quantum libera a CPU imediatamente, e o próximo da fila assume.
  - Se o único processo pronto esgota o quantum, ele continua sem troca de contexto.
  - Registrado como `"rr"`.
- **Validação (slides, quantum=2):** `tt=8,4` / `tw=5,6` / 7 trocas.
- **Oráculo do enunciado (quantum=2):** entrada `0 5 2 / 0 2 3 / 1 4 1 / 3 3 4` deve reproduzir exatamente o diagrama do PDF (execução: P1 P1 P2 P2 P3 P3 P1 P1 P4 P4 P3 P3 P1 P4, em 14 segundos), com `tt=9,75`, `tw=6,25` e 7 trocas.

### 3.2 🔧 Round-Robin com prioridade e envelhecimento
- **História:** Como usuário, quero um Round-Robin em que a escolha do próximo processo considere prioridade dinâmica com envelhecimento, para equilibrar justiça e importância.
- **Regras do enunciado:** o envelhecimento ocorre **a cada quantum**, e **não há preempção por prioridade**.
- **Critérios de aceitação:**
  - Requer `quantum` e `aging`; erro claro se ausentes.
  - Cada processo tem prioridade dinâmica (`pd`), que **inicia igual à estática** ao ingressar.
  - Um processo que chega no meio de um quantum **não interrompe** quem está executando.
  - A cada fronteira de quantum (quantum esgotado, término antecipado ou CPU ociosa com processos prontos): escolhe-se o pronto de maior `pd`, com empates resolvidos pela regra do enunciado; o escolhido tem `pd` restaurada para a estática; todos os demais prontos recebem `pd += aging` (algoritmo do slide 120).
  - O processo cujo quantum esgotou volta ao conjunto de prontos com `pd` igual à estática e concorre à próxima escolha.
  - Registrado como `"rr_prio_aging"`.
- **Validação:** o slide 122 (RR com quantum 1 e prioridades 1, 2, 3, com e sem envelhecimento) é o teste visual mais próximo do algoritmo 7. O slide 121 (PRIOd) é preemptivo e serve apenas como comparação aproximada.
- **Decisão a confirmar:** a nota de revisão do projeto adota "só quem espera ganha aging ao completar um quantum" (sem incremento no ócio, na primeira seleção ou em término antecipado). Se a equipe mantiver essa variante, deve justificá-la no documento de decisões. Se preferir seguir o slide 120, aplicar a regra acima. Em caso de dúvida, perguntar ao professor.

### 3.3 Esqueleto da aplicação gráfica (bônus)
- Janela principal com painéis de entrada, configuração, resultados e diagrama, e botão "Executar" (Tkinter + ttk, sem dependências externas). Validação do fluxo com chamada mockada.

### 3.4 Entrada de processos e configuração na interface
- Tabela editável (instante, duração, prioridade) com adicionar/remover, campos `quantum` e `aging`.
- Mesmas validações da história 1.3, com mensagens visuais.
- Opcional: carregar de arquivo com os leitores do Épico 1.

### 3.5 Controlador
- `controlador.py` lê os widgets, monta `Configuracao` e processos, executa todos os algoritmos **via fábrica** e guarda os `ResultadoSimulacao`.
- A GUI nunca instancia algoritmos diretamente.
- Os resultados da GUI devem coincidir com os da CLI para a mesma entrada e a mesma semente.

### 3.6 Widget de resultados
- Métricas (tt, tw, trocas) por algoritmo lado a lado e tabela-resumo no estilo do "Quadro Comparativo".

### 3.7 Gantt animado (bônus)
- `Canvas` com uma barra colorida por processo, avanço tick a tick com `after()`, lendo do `DiagramaTempo`, e controles de play/pause/velocidade, se o tempo permitir.