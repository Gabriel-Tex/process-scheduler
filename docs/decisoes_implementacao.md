# Decisões de Implementação

## Sumário
* [`src/scheduler/domain/process.py`: Entidades de Domínio e Gestão de Estado](#srcschedulerdomainprocesspy-entidades-de-domínio-e-gestão-de-estado)
* [`src/scheduler/domain/configuration.py`: Configurações Globais da Simulação](#srcschedulerdomainconfigurationpy-configurações-globais-da-simulação)
* [`src/scheduler/schedulers/base.py`: Interface dos Escalonadores e Regra de Desempate](#srcschedulerschedulersbasepy-interface-dos-escalonadores-e-regra-de-desempate)
* [`src/scheduler/schedulers/factory.py`: Fábrica de Escalonadores](#srcschedulerschedulersfactorypy-fábrica-de-escalonadores)
* [`src/scheduler/io/input_reader.py`: Leitura da Entrada Padrão](#srcschedulerioinput_readerpy-leitura-da-entrada-padrão)
* [`src/scheduler/io/config_reader.py`: Leitura do Arquivo de Configuração](#srcschedulerioconfig_readerpy-leitura-do-arquivo-de-configuração)
* [`src/scheduler/simulator/diagram.py`: Diagrama de Tempo](#srcschedulersimulatordiagrampy-diagrama-de-tempo)
* [`src/scheduler/simulator/result.py`: Cálculo de Métricas e Resultado Consolidado](#srcschedulersimuladorresultpy-cálculo-de-métricas-e-resultado-consolidado)

---

## `src/scheduler/domain/process.py`: Entidades de Domínio e Gestão de Estado

Esta secção documenta as decisões de arquitetura e padrões de projeto aplicadas ao núcleo do simulador, especificamente às estruturas que representam os processos (ou tarefas) e o seu ciclo de vida. O objetivo principal é garantir um modelo de domínio robusto, validado e independente da lógica dos algoritmos de escalonamento.

### 1. Utilização de `@dataclass` para a Entidade Principal
A classe `Processo` foi implementada utilizando o decorador `@dataclass` do Python. Esta decisão técnica foi tomada pelos seguintes motivos:
* **Redução de *Boilerplate*:** Elimina a necessidade de escrever um método `__init__` repetitivo apenas para atribuição de variáveis.
* **Facilidade de Depuração (Debug):** O `@dataclass` gera automaticamente um método `__repr__`, permitindo que qualquer `print(processo)` durante os testes de mesa ou validação dos algoritmos imprima o estado completo e legível do objeto em formato de *string* (ex: `Processo(id='P1', tempo_processamento=5...)`), em vez do endereço de memória genérico.
* **Imutabilidade Estrutural:** Facilita a separação rigorosa entre os dados que o utilizador fornece e os dados que o sistema controla internamente.

### 2. Separação Estrita de Atributos (Campos de Entrada vs. Campos Geridos)
Para evitar que o motor de simulação ou os escalonadores corrompam o estado inicial do processo, os atributos foram divididos em duas categorias claras:
* **Campos de Entrada:** `id`, `instante_criacao`, `tempo_processamento` e `prioridade_estatica`. Correspondem exatamente às três informações exigidas na entrada de dados: instante de criação, duração em segundos e prioridade estática.
* **Campos Geridos (`init=False`):** Utilizou-se `field(init=False)` para atributos como `tempo_restante`, `prioridade_dinamica`, `status`, `instante_inicio` e `instante_termino`. Isto impede a injeção destes valores no construtor. O estado dinâmico é inteiramente gerido pela própria classe (encapsulamento) e pelo motor do simulador à medida que o tempo avança.

### 3. Suporte Nativo a Prioridades Dinâmicas e Envelhecimento (*Aging*)
Há necessidade de lidar com inanição (*starvation*) através do aumento proporcional da prioridade (envelhecimento).
* Para suportar o algoritmo de Round-Robin com prioridade e envelhecimento, a classe armazena explicitamente a `prioridade_estatica` (imutável) e a `prioridade_dinamica` (variável).
* Na instanciação da tarefa, a `prioridade_dinamica` é automaticamente inicializada com o valor da prioridade fixa, garantindo que a entidade nasce pronta para algoritmos que aplicam *aging*. Assumiu-se a convenção de que um maior valor numérico representa uma maior prioridade.

### 4. Validação *Fail-Fast* no `__post_init__`
Para garantir a integridade dos dados antes do início da simulação, implementou-se um método `__post_init__`. Este método atua como uma barreira de segurança:
* Valida se o `tempo_processamento` é estritamente superior a zero.
* Assegura que o `instante_criacao` e a `prioridade_estatica` não são valores negativos.
* Se um ficheiro de entrada contiver dados inválidos, a aplicação falha imediatamente na leitura com um `ValueError` descritivo, evitando que a simulação corra com estados inconsistentes e produza métricas erradas no final.

### 5. Máquina de Estados Finita (`StatusProcesso`)
O ciclo de vida do processo foi modelado com um `Enum` chamado `StatusProcesso`, mapeando os diferentes momentos de alocação e espera:
* **`NOVO`**: Estado inicial antes de atingir o tempo de ingresso.
* **`PRONTO`**: A aguardar atribuição do processador na fila.
* **`EXECUTANDO`**: A ocupar o processador e a consumir o seu tempo de execução (ou *quantum*).
* **`FINALIZADO`**: Quando a duração chega ao fim e a tarefa é dada como terminada.
O uso de um `Enum` com `auto()` previne o uso de *strings* soltas no código, evitando erros de digitação e facilitando comparações seguras no motor de escalonamento.

### 6. Encapsulamento do Comportamento (`executar_um_tick` e `finalizado`)
A lógica de passagem de tempo foi internalizada na classe:
* **`executar_um_tick()`**: Centraliza a lógica de dedução de tempo. Sempre que chamado, reduz o `tempo_restante` e verifica autonomamente se chegou a zero, transitando o seu próprio estado para `FINALIZADO`. Se for chamado num processo já terminado, levanta um `RuntimeError`.
* **`@property finalizado`**: Uma abstração sintática para evitar que as classes dos algoritmos de escalonamento precisem importar e comparar repetidamente `processo.status == StatusProcesso.FINALIZADO`, podendo assim apenas chamar `processo.finalizado`. Isso promove legibilidade e encapsula a lógica de estado.

## `src/scheduler/domain/configuration.py`: Configurações Globais da Simulação

Este arquivo isola a estrutura responsável por armazenar os parâmetros de configuração exigidos para a parametrização dos algoritmos, especificamente o valor do *quantum* e a taxa de envelhecimento (*aging*).

### 1. Estrutura Simples com `@dataclass`
Foi escolhida novamente a abstração `@dataclass` para criar um objeto de transferência de dados simples. Isso evita o uso de variáveis globais ou dicionários soltos (`dict`) para carregar as configurações lidas do ficheiro de texto plano, garantindo tipagem forte (`int`) e acesso estruturado, limpo e legível (ex: `config.quantum`, `config.aging`).

### 2. Uniformidade da Interface do Motor (Polimorfismo)
A decisão arquitetural mais importante atrelada a este arquivo é o seu uso universal. Embora o *quantum* e o *aging* sejam parâmetros exclusivos dos algoritmos da família *Round-Robin*, o objeto `Configuracao` é instanciado e injetado no construtor de **todos** os escalonadores (incluindo FCFS, SJF, etc.). 
* **Porquê?** Isso permite que a Fábrica de Escalonadores e o Motor de Simulação interajam com qualquer algoritmo utilizando exatamente a mesma assinatura base: `Escalonador(configuracao)`. Os algoritmos que não precisam destes parâmetros simplesmente os ignoram. Esta decisão mantém o motor limpo, polimórfico e estritamente livre de blocos `if/else` para checar qual algoritmo está a ser executado.

### 3. Valores Padrão (*Fallback* Seguro)
Os atributos foram declarados com os valores padrão `quantum: int = 2` e `aging: int = 1`. Estes valores refletem exatamente o cenário de exemplo fornecido no enunciado da tarefa. Isto confere resiliência à aplicação: caso haja alguma inconsistência na leitura parcial do ficheiro de texto, a estrutura garante um estado base perfeitamente válido para a simulação prosseguir sem lançar exceções inesperadas.

### 4. Alinhamento com o Modelo Matemático (Fator Alfa)
O atributo `aging` modela o incremento de prioridade aplicado às tarefas que aguardam na fila. No contexto do código, este atributo traduz diretamente a fórmula $pd_i \leftarrow pd_i + \alpha$.

## `src/scheduler/schedulers/base.py`: Interface dos Escalonadores e Regra de Desempate

Esta secção documenta as decisões relativas ao contrato abstrato que todos os algoritmos de escalonamento devem respeitar, bem como à função centralizada de desempate. Juntas, estas duas peças garantem que o motor de simulação possa orquestrar qualquer algoritmo de forma uniforme e que a resolução de empates seja consistente em todo o projecto.

### 1. Classe Abstrata como Contrato (`EscalonadorBase`)
Optou-se por uma classe base abstrata (`abc.ABC`) em vez de um protocolo (`typing.Protocol`) ou de uma interface informal. A razão principal é a necessidade de fornecer **implementações padrão** (*no-op*) para dois dos três métodos do contrato:
* **`ao_chegar(processo, tempo)`**: Implementação padrão vazia. Apenas os algoritmos que mantêm uma estrutura interna de fila (todos, na prática) precisam sobrescrevê-lo. Mantê-lo como *no-op* permite que uma subclasse mínima (útil em testes) funcione sem ter de definir este método.
* **`selecionar_proximo(tempo, em_execucao)`**: O único método marcado com `@abstractmethod`. É o ponto de diferenciação entre os algoritmos. Cada um decide quem ocupa a CPU segundo a sua política própria (ordem de chegada, menor duração, maior prioridade, fila circular, etc.).
* **`ao_finalizar_tick(tempo, em_execucao)`**: Implementação padrão vazia. Funciona como *hook* de fim de tick, usado exclusivamente pelos algoritmos da família Round-Robin (contagem de *quantum* e incremento de envelhecimento). Os restantes algoritmos herdam o *no-op* sem qualquer custo.

### 2. Contrato de Três Métodos - Nem Mais, Nem Menos
O motor de simulação opera num ciclo fixo a cada tick: processar chegadas → selecionar próximo → executar → hook de fim de tick. Os três métodos de `EscalonadorBase` espelham exactamente este ciclo. Não se adicionou um método `ao_finalizar_processo()` na interface pública porque a remoção de processos finalizados das estruturas internas dos escalonadores pode ser resolvida dentro dos próprios métodos já existentes (`selecionar_proximo` ou `ao_finalizar_tick`), sem necessidade de alargar o contrato.

### 3. Regra de Desempate como Função Livre (`desempatar`)
A regra de desempate foi implementada como uma **função de módulo** e não como um método de `EscalonadorBase`, pelas seguintes razões:
* **Sem estado**: a função é pura - recebe candidatos, observa-os e devolve um vencedor, sem qualquer efeito colateral nem necessidade de aceder a `self`.
* **Ponto único**: implementar a regra numa só localização garante que os três critérios (preferir quem já está na CPU → menor `tempo_restante` → aleatório) sejam aplicados de forma idêntica por todos os sete algoritmos, eliminando o risco de divergências subtis entre implementações.

### 4. Ordem dos Critérios de Desempate
A função aplica os critérios na sequência definida pelo enunciado:
1. **Processo já na CPU** - evitar trocas de contexto desnecessárias. A comparação usa `is` (identidade de objecto) em vez de `==` (igualdade de valor), porque dentro de uma mesma execução de simulação cada `Processo` é uma instância única e irrepetível.
2. **Menor `tempo_restante`** - favorece a conclusão rápida de processos com pouco tempo restante, comportamento coerente com a filosofia do SRTF.
3. **Aleatório** - último recurso, necessário para que a simulação produza um resultado definido mesmo em cenários de empate absoluto.

### 5. Injeção de Aleatoriedade (`random.Random` por Parâmetro)
A função `desempatar` nunca utiliza o módulo `random` global (ex.: `random.choice`). Em vez disso, recebe uma instância de `random.Random` como parâmetro. Esta decisão é essencial para:
* **Reprodutibilidade em testes**: ao fixar a *seed* (`random.Random(42)`), obtemos resultados determinísticos que podem ser comparados com os valores de referência dos slides.
* **Isolamento entre execuções**: cada chamada à fábrica pode fornecer uma instância de `Random` independente, evitando que a ordem de execução dos algoritmos (FCFS antes de SJF, etc.) afecte os desempates de outro algoritmo.

### 6. Optimização para Caso Unitário
Quando a lista de candidatos contém apenas um elemento, a função devolve-o directamente sem invocar nenhum dos três critérios. Isto garante que chamadas ao `random.Random` só ocorrem quando há de facto uma escolha a fazer, preservando a sequência de números aleatórios para os empates reais e mantendo o comportamento 100% determinístico nos casos sem ambiguidade.

## `src/scheduler/schedulers/factory.py`: Fábrica de Escalonadores

Esta secção documenta as decisões relativas ao ponto central de instanciação de algoritmos. A fábrica isola por completo o conhecimento sobre as classes concretas dos escalonadores, permitindo que a CLI, a GUI e o motor operem exclusivamente com nomes (*strings*) e com a interface abstracta `EscalonadorBase`.

### 1. Registro Dinâmico com Função Explícita (`registrar`)
A fábrica começa vazia e é populada por chamadas explícitas a `registrar(nome, construtor)`, tipicamente feitas ao nível de módulo de cada ficheiro de algoritmo (ex.: `fcfs.py`). Optou-se por uma função explícita em vez de um decorador de classe pelos seguintes motivos:
* **Clareza de intenção**: o registo é uma acção visível e auditável no código, não um efeito colateral implícito de importação.
* **Flexibilidade**: o construtor registado não precisa de ser a classe directamente - pode ser uma *factory function* que adicione lógica de inicialização antes de devolver a instância.

### 2. Assinatura Uniforme dos Construtores (`Configuracao, random.Random`)
Todo construtor registado na fábrica deve aceitar dois parâmetros: `Configuracao` e `random.Random`. Algoritmos que não precisam de *quantum*, *aging* ou aleatoriedade (ex.: FCFS) simplesmente ignoram estes parâmetros internamente. Esta uniformidade permite que a função `criar()` instancie qualquer algoritmo com exactamente a mesma chamada, sem blocos `if/else` por tipo de algoritmo. É a mesma decisão de polimorfismo documentada na secção de `configuration.py` (§2), aplicada agora ao nível da fábrica.

### 3. Protecção contra Registos Duplicados
A função `registrar()` levanta `ValueError` se o nome já existir no registo. Isto detecta erros de integração (dois módulos tentando registar o mesmo nome) no momento da importação, em vez de silenciosamente substituir um algoritmo por outro.

### 4. Mensagem de Erro Descritiva em `criar()`
Quando o nome solicitado não está registado, a `ValueError` inclui a lista de todos os algoritmos disponíveis. Isto é especialmente útil para o utilizador da CLI, que pode ter digitado um nome incorrecto (ex.: `rr_aging` em vez de `rr_prio_aging`), e torna a mensagem de erro auto-documentada.

### 5. *Fallback* para `random.Random()` Não-Determinístico
Se a função `criar()` for chamada sem fornecer uma instância de `random.Random`, ela cria automaticamente uma com *seed* não-determinística. Isto garante que a utilização em produção (CLI sem `--seed`) funcione sem configuração adicional, enquanto os testes e validações manuais podem injectar uma *seed* fixa para reprodutibilidade.

### 6. `listar_algoritmos()` Preserva a Ordem de Inserção
A função devolve os nomes na ordem em que foram registados, aproveitando a garantia de ordenação dos dicionários do Python 3.7+. A CLI utiliza esta lista para iterar sobre "todos os algoritmos" no modo padrão e para apresentar as opções válidas ao utilizador.

## `src/scheduler/io/input_reader.py`: Leitura da Entrada Padrão

Esta secção documenta as decisões relativas à transformação do texto de entrada (uma linha por processo, três inteiros separados por espaços) em objectos `Processo` do domínio. O módulo é responsável exclusivamente pelo *parsing* e pela validação estrutural — não executa simulação, não imprime resultados e não lê ficheiros de configuração.

### 1. Recepção do Fluxo por Parâmetro (`TextIO`)
A função `ler_processos` recebe o fluxo de texto como parâmetro (`TextIO`) em vez de chamar `sys.stdin` directamente. Esta decisão desacopla a lógica de *parsing* da fonte concreta de dados:
* A camada de CLI (história futura) é quem decide que a fonte é `sys.stdin`.
* Para verificação manual ou testes, basta passar `io.StringIO("0 5 2\n0 2 3")` — sem necessidade de redirecionamento de terminal ou *mocking* de `sys`.

### 2. Excepção Própria (`EntradaInvalidaError`)
Foi definida uma subclasse de `ValueError` específica para erros de *parsing* da entrada. Isto permite que a CLI (implementada numa história posterior) trate erros de entrada de forma diferenciada de outros `ValueError` do sistema (ex.: erros de domínio internos), oferecendo mensagens de erro mais contextualizadas ao utilizador final.

### 3. IDs Atribuídos por Ordem de Leitura (Nunca por `instante_criacao`)
Os identificadores `P1`, `P2`, `P3`, … são atribuídos sequencialmente na ordem em que cada linha não vazia é lida. Conforme o PDF da atividade explicita, "essa listagem não precisa necessariamente estar ordenada por data de criação" — logo o módulo **nunca** reordena a entrada antes de atribuir IDs. O contador de IDs só é incrementado para linhas com conteúdo (linhas em branco não consomem IDs).

### 4. Divisão com `str.split()` sem Argumentos
A escolha de `str.split()` (sem argumento separador) é deliberada: divide por **um ou mais** caracteres de espaço em branco consecutivos (espaços, tabs, etc.), cobre automaticamente o requisito do PDF ("inteiros separados por um ou mais espaços em branco") e também descarta espaços no início e no fim da *string* — tornando desnecessário um `.strip()` prévio no conteúdo já guardado.

### 5. Numeração de Linhas 1-Based com `enumerate(..., start=1)`
Todas as mensagens de erro reportam o número da linha como um humano o leria no ficheiro (começando em 1, não em 0). Isto é especialmente útil quando o professor testa o simulador com conjuntos de dados maiores e precisa localizar rapidamente uma entrada inválida.

### 6. Não Duplicação da Validação de Domínio
O módulo não replica as verificações que já existem em `Processo.__post_init__` (ex.: `tempo_processamento > 0`, `instante_criacao >= 0`). Essas violações são deixadas propagar naturalmente até ao `ValueError` do construtor de `Processo`, que é então embrulhado numa `EntradaInvalidaError` com o número da linha acrescentado. Isto garante um ponto único de verdade para regras de domínio e evita inconsistências se as regras forem alteradas no futuro.

### 7. Linhas em Branco Ignoradas Silenciosamente
Linhas que contêm apenas espaços, tabs ou nenhum caractere são ignoradas sem erro. Esta decisão é pragmática: ficheiros de texto frequentemente contêm linhas vazias no final ou entre blocos de dados, e tratá-las como erro seria uma fonte desnecessária de frustração para o utilizador.

### 8. Tratamento de Inteiros com Sinal
A conversão via `int()` do Python aceita naturalmente sinais explícitos (ex.: `+5`, `-1`). Valores negativos que violem regras de domínio (ex.: `instante_criacao = -1`) são rejeitados pelo `Processo.__post_init__`, não pelo *parser*. Valores positivos com sinal explícito (`+5`) são aceites como equivalentes a `5`. Esta é a semântica nativa de `int()` e não foi restrita por não haver qualquer indicação no enunciado de que sinais explícitos devam ser proibidos.

## `src/scheduler/io/config_reader.py`: Leitura do Arquivo de Configuração

Esta secção documenta as decisões relativas à transformação do ficheiro de configuração em texto plano (formato `chave:valor`) num objecto `Configuracao` do domínio. O módulo é responsável exclusivamente pelo *parsing*, pela validação estrutural e pela validação de valores — não lê processos, não executa simulação e não imprime resultados.

### 1. Recepção do Arquivo por Parâmetro (`TextIO`)
Tal como no leitor de entrada (história 1.3), a função `ler_configuracao` recebe o ficheiro já aberto como `TextIO`, em vez de receber um caminho e chamar `open()` internamente. A decisão de *onde* está o ficheiro (caminho padrão, argumento de linha de comando, etc.) pertence à camada de CLI. Para verificação manual, basta passar `io.StringIO("quantum:2\naging:1")`.

### 2. Excepção Própria (`ConfiguracaoInvalidaError`)
Foi definida uma subclasse de `ValueError` específica para erros de leitura/validação de configuração. Isto permite que a CLI trate erros de configuração de forma diferenciada de erros de entrada de processos (`EntradaInvalidaError`) ou de outros `ValueError` internos do sistema.

### 3. Chaves Desconhecidas Tratadas como Erro
Uma chave que não seja `quantum` nem `aging` levanta `ConfiguracaoInvalidaError` imediatamente, em vez de ser ignorada. A razão é pragmática: como o ficheiro é escrito à mão, uma chave desconhecida quase certamente indica um erro de digitação (ex.: `quantun:2`). Ignorá-la silenciosamente faria a simulação correr com valores padrão, produzindo resultados errados sem nenhum aviso — um tipo de falha particularmente difícil de diagnosticar.

### 4. Chaves Repetidas Tratadas como Erro
Se a mesma chave aparecer mais de uma vez no ficheiro (ex.: `quantum:2` seguido de `quantum:4`), o módulo levanta erro em vez de silenciosamente usar o último valor. Um ficheiro com chaves repetidas é ambíguo e, tal como com chaves desconhecidas, é preferível falhar explicitamente do que correr com uma configuração possivelmente incorrecta.

### 5. Ambas as Chaves São Obrigatórias
Ao final da leitura, o módulo verifica que tanto `quantum` quanto `aging` foram fornecidos. A ausência de qualquer uma delas levanta `ConfiguracaoInvalidaError` indicando qual chave está em falta. Embora `Configuracao` tenha valores padrão (`quantum=2`, `aging=1`), optou-se por exigir ambas no ficheiro para evitar erros silenciosos: se o utilizador criou um ficheiro de configuração, é razoável esperar que ele defina os dois parâmetros explicitamente.

### 6. Validação de Valores Positivos no Leitor (Não no Domínio)
O módulo valida que `quantum > 0` e `aging > 0` directamente, porque a dataclass `Configuracao` não possui `__post_init__` com validação (aceita qualquer inteiro). Esta decisão concentra a validação de limites no ponto de entrada dos dados (o *parser*), que é onde as mensagens de erro com número de linha são mais úteis. Se futuramente se adicionar validação a `Configuracao.__post_init__`, a duplicação pode ser removida deste módulo — por enquanto, não há risco de inconsistência.

### 7. Separação com `str.split(":", maxsplit=1)`
O uso de `maxsplit=1` garante que apenas a primeira ocorrência de `:` é usada como separador. Embora os valores esperados sejam inteiros (sem `:` no valor), esta precaução torna o *parser* robusto contra extensões futuras sem custo de complexidade.

### 8. Normalização de Chaves para Minúsculas
As chaves são convertidas para minúsculas antes da comparação (`chave.strip().lower()`), tornando a leitura *case-insensitive* — `Quantum:2`, `QUANTUM:2` e `quantum:2` são todos aceites. Esta decisão é pragmática: como o ficheiro é editado manualmente, é comum o utilizador variar a capitalização, e rejeitar `Quantum` por não ser exactamente `quantum` seria uma fonte desnecessária de frustração.

### 9. Suporte a Comentários (`#`)
Linhas iniciadas por `#` (após remoção de espaços iniciais) são tratadas como comentários e ignoradas silenciosamente. O PDF da atividade não menciona comentários no ficheiro de configuração, mas o ficheiro de exemplo do projecto (`config/config.txt`) já contém linhas de comentário. Esta funcionalidade foi adicionada como conveniência sem custo de complexidade, e está documentada aqui por não ser um requisito explícito do enunciado.

## `src/scheduler/simulator/diagram.py`: Diagrama de Tempo

Esta secção documenta as decisões relativas à classe `DiagramaTempo`, responsável por acumular o estado de cada tick de simulação e renderizar o diagrama de tempo no formato de texto exigido pelo PDF da atividade. A classe é puramente de apresentação — não sabe o que é um `Processo`, não decide nada sobre escalonamento e não calcula métricas.

### 1. Independência Total do Domínio
`DiagramaTempo` não importa nada de `dominio/`, `escalonadores/`, `io/`, `cli/` ou `gui/`. Trabalha exclusivamente com `str` (ids de processos) e coleções da biblioteca padrão (`frozenset`, `list`). Esta independência é deliberada: permite testar o diagrama isoladamente, sem precisar de instanciar `Processo`, executar escalonadores ou simular o motor. Basta chamar `registrar_tick` manualmente com valores inventados.

### 2. Ordem das Colunas Fixada na Criação
O construtor recebe a lista de ids dos processos na ordem em que devem aparecer como colunas (tipicamente `P1, P2, P3, …`, na ordem de leitura da entrada). Esta ordem é imutável após a criação. A alternativa — descobrir colunas dinamicamente à medida que os ticks são registados — causaria problemas: a ordem das colunas dependeria da ordem em que os processos chegam ou terminam, o que tornaria o diagrama imprevisível e difícil de comparar com a referência do PDF.

### 3. Tempo Implícito pela Ordem das Chamadas
O método `registrar_tick` não recebe o número do tick como parâmetro. A primeira chamada corresponde ao tick 0, a segunda ao tick 1, e assim por diante. Esta simplificação elimina a possibilidade de registar ticks fora de ordem ou com buracos, e reduz a interface ao mínimo necessário — o motor (implementado noutra história) apenas chama `registrar_tick` a cada iteração do seu laço.

### 4. Duas Informações por Tick: `executando` + `presentes`
Cada tick é representado por duas informações já resolvidas pelo motor: quem está na CPU (`executando`, um `str` ou `None`) e o conjunto de ids que já chegaram e ainda não terminaram (`presentes`). A classe não precisa de saber tempo restante, prioridade ou qualquer outro atributo de `Processo` — toda a lógica de escalonamento já foi decidida antes.

### 5. Regra das Três Células
A renderização aplica a regra do PDF com prioridade explícita:
1. Se o id é igual a `executando` → `##` (independentemente de estar em `presentes`).
2. Se o id está em `presentes` mas não é `executando` → `--`.
3. Se o id está ausente de `presentes` e não é `executando` → célula em branco.

O critério 1 tem prioridade sobre o critério 2 por design: `executando` pode ou não aparecer em `presentes` (dependendo de como o motor implementa a lógica), e o diagrama produz o resultado correcto em ambos os casos.

### 6. Armazenamento com `frozenset`
Os ids presentes de cada tick são convertidos para `frozenset` no momento do registo, em vez de guardar o iterável original. Isto garante: (a) imutabilidade — nenhuma alteração posterior ao conjunto externo afecta o diagrama; (b) operações de pertença (`in`) em tempo $O(1)$ durante a renderização.

### 7. Colunas de Largura Dinâmica
Cada coluna de processo tem largura igual a `max(2, len(id))` — 2 é o mínimo para caber `##` e `--`, e ids mais longos (ex.: `P10`, `P100`) expandem a coluna automaticamente. A coluna de tempo também se ajusta ao rótulo mais largo (`0-1` vs `99-100`). As colunas são separadas por dois espaços e alinhadas à direita, garantindo um alinhamento consistente independentemente do número de ticks ou processos.

### 8. Zero Ticks Produz Apenas o Cabeçalho
Chamar `renderizar()` sem ter registado nenhum tick devolve apenas a linha de cabeçalho (`tempo  P1  P2  …`), sem lançar erro. Isto é útil para cenários de teste e evita tratar um caso especial no motor ("se não houver processos, não renderize").
## `src/scheduler/simulator/result.py`: Cálculo de Métricas e Resultado Consolidado

Esta secção documenta as decisões de implementação relativas ao cálculo das métricas de simulação e sua consolidação num único objeto. As métricas calculadas incluem tempo médio de execução (turnaround), tempo médio de espera (waiting time) e número de trocas de contexto, de acordo com o exigido pela atividade e validado contra os exemplos dos slides.

### 1. Separação em Funções Puras
A lógica de cálculo foi isolada em funções independentes e puras (`calcular_tempos_medios` e `contar_trocas_contexto`) e uma função agregadora (`construir_resultado`), em vez de serem métodos da própria dataclass ou do motor. Esta decisão facilita os testes unitários isolados, visto que é possível validar as fórmulas simulando processos ou vetores de contexto arbitrariamente sem necessitar de uma simulação completa.

### 2. Validação de Pré-condições em `calcular_tempos_medios`
A função responsável por extrair os tempos de execução (tt) e espera (tw) garante que:
* A lista de processos passada não é vazia. O retorno de um tuplo nulo ou zeros mascararia problemas de chamadas indevidas no sistema.
* Todos os processos recebidos estejam efetivamente finalizados. O cálculo efetuado depende da propriedade calculada `instante_termino`, e caso o processo não tivesse finalizado, a geração do turnaround não seria representativa do término, produzindo métricas incorretas sem nenhum aviso. O uso de excepções do tipo `ValueError` sinaliza violações do contrato estrito.

### 3. Fórmulas Explícitas Baseadas nos Slides
O turnaround time foi padronizado como sendo a diferença entre `instante_termino` e `instante_criacao`. Por sua vez, o waiting time (espera) foi computado como a subtração `turnaround - tempo_processamento` (duração). Esta métrica padronizada segue a mesma que os slides de algoritmos da disciplina comprovam em todos os seus quadros de execução. Ambas originam a média aritmética dividida pela quantidade de processos, resultando nas métricas pedidas.

### 4. Regra de Contagem de Trocas de Contexto
A função `contar_trocas_contexto` atende rigorosamente à definição de que trocas de contexto são contabilizadas apenas em substituições consecutivas de alocação de processo à CPU: transições do estado ocioso (`None`) para execução ou saídas para o ócio **não** afetam este total. Esta restrição justifica o seu cálculo a partir de `execucoes[i-1]` contra `execucoes[i]`, que previne intersecções inválidas. Para garantir esta conformidade, transições ociosas intermédias suspendem a contabilização (ex.: `[P1, None, P2]` é ignorado na troca se o critério exigisse trocas diretas em iterador sucessivo). A implementação iterativa foi elaborada especificamente sobre adjacências com restrição nula.

### 5. Dataclass Imutável `ResultadoSimulacao`
A classe responsável por guardar as métricas foi decorada com `@dataclass(frozen=True)` visando garantir integridade total. Ao consolidar um conjunto numérico final de uma simulação (tt, tw, trocas e diagrama), torna-se uma fonte imutável e segura de apresentação. Nenhuma peça do sistema deve ser capaz de adulterar um resultado analítico previamente emitido.
