"""
Entidades de domínio: Processo e StatusProcesso.

Responsabilidades:
- Modelar o estado de um processo durante a simulação.
- Nenhuma lógica de escalonamento aqui — apenas dados e validações simples.

Campos de Processo:
    id              — identificador sequencial atribuído na ordem de leitura (P1, P2, …)
    instante_criacao— tick em que o processo chega na fila de prontos (≥ 0)
    duracao         — tempo total de CPU necessário (> 0)
    prioridade_estatica — prioridade original, imutável durante a simulação (≥ 0)
    prioridade_dinamica — prioridade corrente (modificada pelo envelhecimento no RR_aging)
    tempo_restante  — unidades de CPU que ainda faltam executar
    status          — StatusProcesso atual

StatusProcesso (enum):
    NAO_CHEGOU  — instante_criacao ainda não foi alcançado
    PRONTO      — na fila de prontos, aguardando CPU
    EXECUTANDO  — ocupando a CPU neste tick
    FINALIZADO  — tempo_restante == 0

Convenção de prioridade:
    Maior valor numérico = maior prioridade (conforme slides do professor).
    Esta suposição está documentada em docs/decisoes_implementacao.md.
"""
