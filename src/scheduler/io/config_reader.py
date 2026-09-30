"""
Leitura do arquivo de configuração (quantum / aging).

Transforma um ficheiro de texto plano no formato ``chave:valor`` (uma por
linha) num objecto ``Configuracao`` do domínio. Não faz impressão, não lê
processos e não executa simulação.

Formato esperado::

    quantum:2
    aging:1

Espaços extras ao redor de chave, ``:`` e valor são tolerados.
Linhas em branco e linhas iniciadas por ``#`` (comentários) são ignoradas.
"""

from __future__ import annotations
from typing import TextIO
from src.scheduler.domain.configuration import Configuracao


# Chaves reconhecidas pelo ficheiro de configuração.
_CHAVES_VALIDAS: frozenset[str] = frozenset({"quantum", "aging"})


class ConfiguracaoInvalidaError(ValueError):
    """
    Erro de parsing ou validação do arquivo de configuração.

    Levantado quando o arquivo não pode ser convertido num ``Configuracao``
    válido - seja por formato incorreto, chaves desconhecidas/ausentes/repetidas
    ou valores fora dos limites esperados.

    A mensagem inclui o número da linha (1-based) sempre que aplicável.
    """


def ler_configuracao(arquivo: TextIO) -> Configuracao:
    """
    Lê um arquivo de configuração e devolve um ``Configuracao``.

    Args:
        arquivo: Qualquer objecto compatível com ``TextIO`` (ex.:
            ``open("config.txt")``, ``io.StringIO(...)``). Quem decide a
            fonte concreta é a camada de CLI - este módulo permanece
            desacoplado de ``open()`` e de caminhos de ficheiro.

    Returns:
        ``Configuracao`` com ``quantum`` e ``aging`` lidos do arquivo.

    Raises:
        ConfiguracaoInvalidaError: Se o arquivo estiver incompleto,
            malformado ou contiver valores inválidos.
    """
    valores_lidos: dict[str, int] = {}

    for numero_linha, linha in enumerate(arquivo, start=1):
        conteudo = linha.strip()

        # Linhas em branco e comentários são ignorados silenciosamente.
        if not conteudo or conteudo.startswith("#"):
            continue

        # Separar chave e valor pelo primeiro ':'.
        if ":" not in conteudo:
            raise ConfiguracaoInvalidaError(
                f"Linha {numero_linha}: formato inválido - esperado "
                f"'chave:valor', recebeu '{conteudo}'."
            )

        chave_bruta, valor_bruto = conteudo.split(":", maxsplit=1)
        chave = chave_bruta.strip().lower()
        valor_str = valor_bruto.strip()

        # Chave desconhecida
        if chave not in _CHAVES_VALIDAS:
            raise ConfiguracaoInvalidaError(
                f"Linha {numero_linha}: chave desconhecida '{chave}'. "
                f"Chaves válidas: {', '.join(sorted(_CHAVES_VALIDAS))}."
            )

        # Chave repetida
        if chave in valores_lidos:
            raise ConfiguracaoInvalidaError(
                f"Linha {numero_linha}: chave '{chave}' já foi definida "
                f"anteriormente. Cada chave deve aparecer exatamente uma vez."
            )

        # Conversão para inteiro
        try:
            valor = int(valor_str)
        except ValueError as e:
            raise ConfiguracaoInvalidaError(
                f"Linha {numero_linha}: valor de '{chave}' não é um inteiro "
                f"válido - recebeu '{valor_str}'."
            ) from e

        # Validação de valor: quantum e aging devem ser > 0.
        # Configuracao não faz esta checagem internamente (não tem
        # __post_init__ com validação), então ela é responsabilidade
        # deste módulo.
        if valor <= 0:
            raise ConfiguracaoInvalidaError(
                f"Linha {numero_linha}: '{chave}' deve ser > 0, "
                f"recebeu {valor}."
            )

        valores_lidos[chave] = valor

    # Verificar que ambas as chaves obrigatórias foram fornecidas.
    for chave_obrigatoria in sorted(_CHAVES_VALIDAS):
        if chave_obrigatoria not in valores_lidos:
            raise ConfiguracaoInvalidaError(
                f"Chave obrigatória ausente: '{chave_obrigatoria}'. "
                f"O arquivo deve conter exatamente as chaves: "
                f"{', '.join(sorted(_CHAVES_VALIDAS))}."
            )

    return Configuracao(
        quantum=valores_lidos["quantum"],
        aging=valores_lidos["aging"],
    )
