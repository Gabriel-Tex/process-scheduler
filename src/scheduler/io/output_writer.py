"""
PENDENTE: este arquivo contém apenas planejamento, não implementação.

Escritor de saída formatada — EscritorSaida.

Responsabilidades:
    - Converter List[ResultadoSimulacao] em texto formatado e imprimir em stdout.
    - Para cada algoritmo: imprimir um bloco com diagrama de tempo, tt médio,
      tw médio e número de trocas de contexto.
    - Ao final (modo padrão com todos os algoritmos): imprimir tabela comparativa
      com colunas: algoritmo | tt médio | tw médio | trocas de contexto.

Interface pública:
    EscritorSaida.imprimir_resultado(resultado: ResultadoSimulacao) -> None
        Imprime bloco de UM algoritmo.

    EscritorSaida.imprimir_tabela_comparativa(resultados: list[ResultadoSimulacao]) -> None
        Imprime tabela comparativa de múltiplos algoritmos lado a lado.

Nota: toda formatação de texto fica aqui — escalonadores e motor nunca fazem print().
"""
