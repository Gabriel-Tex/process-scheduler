"""Testes manuais do MotorSimulacao.

Testa a integração do motor com algoritmos mock/stub:
    - Laço de tick correto (chegadas, execução, finalização).
    - Contagem de trocas de contexto (incluindo caso de idle -> primeiro processo).
    - Cálculo de tt e tw para casos simples e verificáveis à mão.
    - Isolamento entre execuções (cópias frescas de Processo).
"""
