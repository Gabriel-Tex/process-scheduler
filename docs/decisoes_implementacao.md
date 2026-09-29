# Decisões de Implementação

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