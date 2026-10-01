"""Formatação e escrita dos resultados da simulação.

Transforma objetos ``ResultadoSimulacao`` em texto legível para a saída
padrão: um bloco por algoritmo e, opcionalmente, uma tabela comparativa.
Não imprime diretamente — recebe o fluxo ``TextIO`` por parâmetro.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TextIO

from src.scheduler.simulator.result import ResultadoSimulacao


def _formatar_numero(valor: float) -> str:
    """Formata com vírgula decimal e 1-2 casas (ex.: 8,0 ou 9,75)."""
    arredondado = round(valor, 2)
    s = f"{arredondado:.2f}".replace(".", ",")
    # Remove o zero final quando há duas decimais (ex.: 9,50 → 9,5),
    # mas preserva quando só há uma (ex.: 8,00 → 8,0).
    if s.endswith("0") and not s.endswith(",0"):
        s = s[:-1]
    return s


def formatar_resultado(resultado: ResultadoSimulacao) -> str:
    """Gera o bloco de texto de um algoritmo (métricas + diagrama)."""
    linhas = [
        f"=== {resultado.nome_algoritmo} ===",
        f"Tempo médio de vida (tt): {_formatar_numero(resultado.tt_medio)}",
        f"Tempo médio de espera (tw): {_formatar_numero(resultado.tw_medio)}",
        f"Número de trocas de contexto: {resultado.trocas_contexto}",
    ]
    linhas.append("Diagrama de tempo:")
    linhas.append(resultado.diagrama)
    linhas.append("")
    return "\n".join(linhas)


def formatar_tabela_comparativa(resultados: Sequence[ResultadoSimulacao]) -> str:
    """Gera a tabela de comparação entre algoritmos."""
    if not resultados:
        raise ValueError("Nenhum resultado para formatar.")

    cabecalhos = ["Algoritmo", "tt", "tw", "Trocas"]
    linhas_dados = []
    for r in resultados:
        linhas_dados.append([
            r.nome_algoritmo,
            _formatar_numero(r.tt_medio),
            _formatar_numero(r.tw_medio),
            str(r.trocas_contexto),
        ])

    # Largura de cada coluna = maior valor entre cabeçalho e dados.
    larguras = [
        max(len(str(item)) for item in col)
        for col in zip(cabecalhos, *linhas_dados)
    ]

    linhas: list[str] = ["Quadro comparativo"]

    # Cabeçalho: nome à esquerda, números à direita.
    cab_fmt = [cabecalhos[0].ljust(larguras[0])]
    cab_fmt += [c.rjust(l) for c, l in zip(cabecalhos[1:], larguras[1:])]
    linhas.append("  ".join(cab_fmt))

    for dados in linhas_dados:
        linha_fmt = [dados[0].ljust(larguras[0])]
        linha_fmt += [v.rjust(l) for v, l in zip(dados[1:], larguras[1:])]
        linhas.append("  ".join(linha_fmt))

    return "\n".join(linhas)


def escrever_resultados(
    resultados: Sequence[ResultadoSimulacao],
    saida: TextIO,
) -> None:
    """Escreve blocos individuais e tabela comparativa (se > 1 resultado)."""
    if not resultados:
        raise ValueError("Nenhum resultado para escrever.")

    blocos = [formatar_resultado(r) for r in resultados]
    texto = "\n".join(blocos)

    if len(resultados) > 1:
        texto += formatar_tabela_comparativa(resultados) + "\n"

    saida.write(texto)
