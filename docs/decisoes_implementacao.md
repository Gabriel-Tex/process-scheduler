# Decisões de Implementação

## `src/scheduler/domain/process.py`: Entidades de Domínio e Gestão de Estado

Esta secção documenta as decisões de arquitetura e padrões de projeto aplicadas ao núcleo do simulador, especificamente às estruturas que representam os processos (ou tarefas) e o seu ciclo de vida. O objetivo principal é garantir um modelo de domínio robusto, validado e independente da lógica dos algoritmos de escalonamento.

### 1. Utilização de `@dataclass` para a Entidade Principal
A classe `Processo` foi implementada utilizando o decorador `@dataclass` do Python. Esta decisão técnica foi tomada pelos seguintes motivos:
* **Redução de *Boilerplate*:** Elimina a necessidade de escrever um método `__init__` repetitivo apenas para atribuição de variáveis.
* **Facilidade de Depuração (Debug):** O `@dataclass` gera automaticamente um método `__repr__`, permitindo que qualquer `print(processo)` durante os testes de mesa ou validação dos algoritmos imprima o estado completo e legível do objeto em formato de *string* (ex: `Processo(id='P1', duracao=5...)`), em vez do endereço de memória genérico.
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

### 6. Encapsulamento do Comportamento (`consumir_segundo` e `finalizado`)
A lógica de passagem de tempo foi internalizada na classe:
* **`consumir_segundo()`**: Centraliza a lógica de dedução de tempo. Sempre que chamado, reduz o `tempo_restante` e verifica autonomamente se chegou a zero, transitando o seu próprio estado para `FINALIZADO`. Se for chamado num processo já terminado, levanta um `RuntimeError`.
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