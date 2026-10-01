# Revisão do projeto — 30/09/2026

## Escopo e conclusão

Revisão do épico 3, das integrações existentes e da documentação. Foram lidos
as duas páginas de **Tarefa 01 - Escalonamento de Processos.pdf** (arquivo em
Downloads), o planejamento, README, documentos, código e testes. O diagrama e
as regras da página 2 também foram conferidos na página renderizada.

Os dois Round-Robin e a GUI têm evidências de funcionamento nos testes abaixo.
**O trabalho completo ainda não está pronto para entrega:** faltam a CLI,
o escritor de stdout e os cinco algoritmos do épico 2. Os arquivos reservados
para essas partes contêm apenas docstrings de planejamento; não são implementações.
A GUI é bônus no PDF e não substitui stdin/stdout.

## Requisitos e evidências

| Requisito / origem | Evidência | Resultado |
|---|---|---|
| Sete algoritmos, PDF p. 1 | Fábrica lista `rr` e `rr_prio_aging` | Dois disponíveis; cinco pendentes |
| Entrada com três inteiros e ordem arbitrária, PDF p. 1 | `io/input_reader.py`, `test_readers.py` e `test_engine.py` | Leitor preserva IDs e aceita chegada fora de ordem; CLI pendente |
| Configuração textual quantum/aging, PDF p. 1 | `io/config_reader.py`, importação GUI e testes de leitores/widgets | Implementado; erros preservam dados |
| RR com quantum, PDF p. 1 | `round_robin.py` e testes de quantum 1/maior, fronteira, ócio e término antecipado | Fila FIFO e reenfileiramento verificados |
| Aging a cada quantum, sem preempção por prioridade, PDF p. 1 | `round_robin_aging.py`, `AgingTests`, testes do motor | Verificado sob a convenção de quantum completo |
| Desempate atual → menor restante → sorteio, PDF p. 2 | `base.desempatar`, testes de aging | Aplicado à seleção por prioridade; ver ressalva FIFO abaixo |
| Médias, trocas e diagrama, PDF p. 2 | `engine.py`, `diagram.py`, `test_engine.py` | Resultado calculado; publicação em stdout pendente |
| Código comentado e decisões, PDF p. 2 | Docstrings, comentários de decisões e `docs/decisoes_implementacao.md` | Revisados; afirmações incorretas corrigidas |
| GUI, bônus no PDF | Widgets, controlador, serviço, testes Tk | Edição, validação, resultados e reprodução verificados |
| Demonstração separada, requisito do usuário | `ServicoDemonstrativo`, identificação persistente e testes | Usa dados fixos explicitamente |
| Preempção, requisito do usuário | Filtro e validação do controlador | Não altera regras dos algoritmos |
| Arquivo portátil na raiz, requisito do usuário | `SimuladorEscalonamento.pyz` | Atualizado e executado isoladamente |

Para o exemplo do PDF, o RR com quantum 2 reproduz a sequência de 14 segundos:
P1, P1, P2, P2, P3, P3, P1, P1, P4, P4, P3, P3, P1, P4.
Tempos de término: 13, 4, 12, 14; esperas: 8, 2, 7, 8.
As médias calculadas são vida 9,75 e espera 6,25, com 7 trocas diretas.
Esses valores foram calculados da entrada, não copiados de médias de slides.

## Correções realizadas

1. **Motor ausente:** a importação adiada lançava erro quando o módulo inteiro
   estava ausente. Agora retorna indisponibilidade e permite abrir a demonstração.
   Uma dependência quebrada dentro do motor continua produzindo erro, para não
   esconder defeitos de integração. Testes cobrem ambas as situações.
2. **Velocidade:** `1x` usava 500 ms por segundo simulado. Agora usa 1000 ms;
   testes conferem também 0,5x, 2x e 4x. O agendamento Tk é nominal, não tempo real.
3. **Verificação portátil:** substituídos asserts do verificador por verificações
   explícitas, que continuam ativas com `python -O`. O indicador de pacote agora
   reconhece `.pyz`, em vez de depender de `sys.frozen` de executáveis Windows.
4. **Documentação:** corrigidas alegações de imutabilidade de Processo, pureza
   do desempate aleatório, validação automática de tipos pela dataclass e padrões
   que supostamente corrigiam arquivos de configuração inválidos. Construtores
   e carregamento da fábrica foram descritos conforme o código real.
5. **Organização:** mantida a estrutura útil; criado `examples/processos_pdf.txt`,
   mapa de pastas no README e este relatório. Arquivos pendentes receberam aviso
   explícito; nenhum algoritmo dos colegas foi implementado ou removido.
6. **Planejamento:** adicionada nota à história 3.2 para esclarecer a divergência
   entre aging por seleção/ociosidade e a convenção efetivamente implementada.

## Decisões e ambiguidades preservadas

- **Quantum e aging positivos:** exigência do planejamento 1.4 e contrato atual.
  O PDF fornece valores de exemplo, mas não define literalmente os limites.
  Quantum zero não foi convertido em execução ilimitada, pois mudaria o RR.
- **Prioridade:** o PDF diz “escala de prioridades positiva”, sem definir direção
  numérica. O projeto admite zero, conforme contrato original e pedido anterior,
  e usa maior número como maior prioridade. Confirmar com a equipe/professor
  se “positiva” exige estritamente maior que zero; não se alterou silenciosamente
  o domínio compartilhado.
- **RR FIFO e desempate:** o exemplo do PDF executa P1 antes de P2, embora ambos
  cheguem em 0 e P2 seja menor. A implementação segue o exemplo e a fila da história
  3.1: chegadas simultâneas entram na ordem da entrada. A regra geral de desempate
  é aplicada ao RR por prioridade. A abrangência dessa regra no RR simples deve
  ser confirmada; aplicá-la indiscriminadamente mudaria o exemplo fornecido.
- **Aging:** somente quem está esperando ao fechar um quantum completo recebe
  incremento, antes da próxima escolha. Não ocorre no primeiro despacho, no ócio
  ou em quantum incompleto. Chegada na fronteira não envelhece retroativamente.
  O PDF não detalha todos esses limites; é uma convenção documentada, não citação.
- **Trocas:** contam transições diretas entre processos distintos; entrar/sair
  do ócio não conta. O PDF não especifica esse detalhe. Mantida a decisão existente.
- **Aleatoriedade:** serviço cria `Random(0)` independente por algoritmo, para
  resultados reproduzíveis. Desempate aleatório não modifica processos, mas
  modifica o estado do gerador.

## Arquitetura e legibilidade

Domínio e leitores independem de Tkinter. Algoritmos implementam EscalonadorBase;
o motor não conhece suas classes. O serviço cria processos, configuração e
escalonador novos por execução e adapta os resultados. Widgets exibem registros
calculados: não escalonam nem calculam métricas. A thread de trabalho não chama Tk;
a thread principal recebe os resultados por fila. O Gantt usa cache de células
visíveis e cancela reprodução ao pausar, reiniciar, trocar resultado ou fechar.

As estruturas existentes são proporcionais ao trabalho: deque para RR, lista
para prioridades mutáveis, dataclasses para dados, fábrica para construção e
protocolo para substituição do serviço. Não foi adicionada dependência externa
nem uma camada de abstração desnecessária. O código do domínio permanece mutável
por contrato; anotações de tipo não substituem validação em runtime.

## Verificações executadas

- `python -B -X utf8 -m unittest discover -s tests`: **69 testes passaram**.
- Um desses testes percorre **80 cenários** dos dois RR e confere duração,
  presenças, término, espera individual, média e trocas diretamente dos registros.
- Testes Tk reais: edição, erro preservando dados, integração com worker,
  demonstração, fallback sem módulo do motor, navegação, cache, rolagem,
  redimensionamento, estilos e quatro velocidades.
- Ponto de entrada `python -m src.scheduler.gui` exercitado via `runpy` com
  fechamento automático após abertura da janela e início do loop Tk.
- `.pyz` executado fora do repositório com `python -I -O ... --verificar ...`:
  `ok: true`, ambos os algoritmos presentes e espera individual de 1 segundo
  no cenário P1=(0,3,1), P2=(1,1,1).
- Todos os fontes Python incluídos no `.pyz` conferidos byte a byte com os atuais.
- `git diff --check`: sem erros de whitespace.

## Limitações

Testes executados no Windows com o Python disponível nesta máquina; Linux,
macOS e Python 3.10 especificamente não foram executados. Requisito de execução:
Python 3.10+ com Tkinter e sessão gráfica. Não foi feita inspeção visual manual
da GUI nesta revisão; testes de widgets não garantem ausência de recortes em
todas as resoluções/escalas. A janela conserva mínimo de 1000×900.

Simulações longas armazenam registros e texto completos; o cache do Gantt não
limita a memória do motor. Ao fechar, o worker daemon não é aguardado. Essas
limitações permanecem adequadas aos exemplos acadêmicos, mas impedem afirmar
capacidade para entradas arbitrariamente grandes.

A revisão não certifica conformidade total da equipe enquanto CLI, stdout,
algoritmos restantes e ambiguidades acima estiverem pendentes. As alterações
foram feitas localmente; nenhum commit ou push foi realizado nesta revisão.
