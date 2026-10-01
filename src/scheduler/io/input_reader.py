"""
Leitura de processos a partir de um fluxo de texto (stdin ou equivalente).

Transforma a entrada textual - uma linha por processo, três inteiros separados
por espaços - em objectos ``Processo`` do domínio. Não faz impressão, não lê
ficheiro de configuração e não executa simulação.

Formato esperado de cada linha:
    <instante_criacao>  <tempo_processamento>  <prioridade_estatica>

Exemplo:
    0 5 2
    0 2 3
    1 4 1
    3 3 4

IDs são atribuídos na ordem de leitura (P1, P2, …), independente do
instante_criacao - a entrada NÃO precisa estar ordenada cronologicamente.
"""

from __future__ import annotations
from typing import TextIO
from src.scheduler.domain.process import Processo


class EntradaInvalidaError(ValueError):
    """
    Erro de parsing da entrada de processos.

    Levantado quando uma linha não pode ser convertida num ``Processo``
    válido - seja por formato incorreto (número de campos, valores não
    inteiros) ou por violação de regras de domínio (propagada a partir
    do ``Processo.__post_init__``).

    A mensagem sempre inclui o número da linha (1-based) para facilitar
    a localização do problema no ficheiro de entrada.
    """


def ler_processos(entrada: TextIO) -> list[Processo]:
    """
    Lê processos a partir de um fluxo de texto e devolve a lista na
    ordem de leitura, com ids ``P1``, ``P2``, …

    Args:
        entrada: Qualquer objecto compatível com ``TextIO`` (ex.:
            ``sys.stdin``, ``io.StringIO``). Quem decide a fonte
            concreta é a camada de CLI - este módulo permanece
            desacoplado de ``sys``.

    Returns:
        Lista de ``Processo`` na ordem de leitura.

    Raises:
        EntradaInvalidaError: Se alguma linha estiver malformada ou
            violar regras de domínio. A mensagem indica qual linha
            causou o problema.
    """
    processos: list[Processo] = []
    contador_id = 0

    for numero_linha, linha in enumerate(entrada, start=1):
        # Linhas totalmente em branco são ignoradas silenciosamente.
        conteudo = linha.strip()
        if not conteudo:
            continue

        # str.split() sem argumentos divide por um ou mais espaços em
        # branco (espaços, tabs).
        partes = conteudo.split()

        if len(partes) != 3:
            raise EntradaInvalidaError(
                f"Linha {numero_linha}: esperados 3 valores "
                f"(instante_criacao, tempo_processamento, prioridade_estatica), "
                f"recebeu {len(partes)}."
            )

        # Conversão para inteiro - valores não numéricos são apanhados aqui.
        try:
            instante_criacao = int(partes[0])
            tempo_processamento = int(partes[1])
            prioridade_estatica = int(partes[2])
        except ValueError as e:
            raise EntradaInvalidaError(
                f"Linha {numero_linha}: valor não é um inteiro válido - {e}."
            ) from e

        # Construção do Processo - a validação de domínio (duração > 0,
        # instante >= 0, prioridade >= 0) é responsabilidade do
        # Processo.__post_init__. Não duplicamos aqui; apenas propagamos
        # o erro com contexto de qual linha originou o problema.
        contador_id += 1
        id_processo = f"P{contador_id}"

        try:
            processo = Processo(
                id=id_processo,
                instante_criacao=instante_criacao,
                tempo_processamento=tempo_processamento,
                prioridade_estatica=prioridade_estatica,
            )
        except ValueError as e:
            raise EntradaInvalidaError(
                f"Linha {numero_linha}: {e}"
            ) from e

        processos.append(processo)

    return processos
