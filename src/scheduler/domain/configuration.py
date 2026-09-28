"""
Dataclass de configuração da simulação.

Responsabilidades:
- Armazenar os parâmetros lidos de config/config.txt.
- Fornecer valores padrão para quando o arquivo não existir.

Campos de Configuracao:
    quantum  — duração da fatia de tempo do Round-Robin (padrão: 2)
    aging    — incremento de prioridade por tick de espera no RR+envelhecimento (padrão: 1)

Nota: embora só rr e rr_prio_aging usem esses valores, a configuração é sempre
lida e repassada a todos os algoritmos para manter a interface do motor uniforme.
"""
