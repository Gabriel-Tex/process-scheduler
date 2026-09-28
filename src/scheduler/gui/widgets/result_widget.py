"""
Widget de resultados — ResultadoWidget (bônus).

Responsabilidades:
    - Exibir as métricas de cada algoritmo executado:
        * tt médio, tw médio, trocas de contexto — em tabela comparativa.
        * Diagrama de tempo textual — em área de texto scrollável por algoritmo.
    - Atualizar-se ao receber novos ResultadoSimulacao do controlador.
    - Expor método atualizar(resultados: list[ResultadoSimulacao]) -> None.
"""
