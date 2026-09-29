"""
Fábrica de escalonadores: padrão Factory.

Único ponto do código onde classes concretas de escalonadores são
instanciadas. CLI e GUI nunca importam classes de algoritmos diretamente;
usam apenas nomes (strings) e chamam ``criar()``.

A fábrica começa vazia. Cada módulo de algoritmo concreto se registra 
chamando ``registrar()``.

Suposições de design:
    - O construtor de cada escalonador recebe ``Configuracao`` e
      ``random.Random`` como parâmetros. Algoritmos que não precisam
      deles (ex.: FCFS) simplesmente os ignoram internamente.
    - A ordem de ``listar_algoritmos()`` é a ordem de inserção dos
      registros (preservada pelo dict do Python 3.7+).
"""

from __future__ import annotations
import random
from collections.abc import Callable
from src.scheduler.domain.configuration import Configuracao
from src.scheduler.schedulers.base import EscalonadorBase


# Tipo do construtor que cada algoritmo deve expor ao se registrar.
# Recebe a configuração global e a fonte de aleatoriedade injetável.
ConstrutoEscalonador = Callable[[Configuracao, random.Random], EscalonadorBase]

# Registro interno. Preenchido por chamadas a registrar().
_registro: dict[str, ConstrutoEscalonador] = {}


def registrar(nome: str, construtor: ConstrutoEscalonador) -> None:
    """
    Registra um algoritmo de escalonamento na fábrica.

    Deve ser chamado uma vez por algoritmo, tipicamente no nível de
    módulo do arquivo que define a classe concreta (ex.: fcfs.py).

    Levanta ``ValueError`` se o nome já estiver registrado — isso indica
    duplicação acidental entre módulos.
    """
    if nome in _registro:
        raise ValueError(
            f"Algoritmo '{nome}' já está registrado na fábrica. "
            f"Verifique se há registros duplicados."
        )
    _registro[nome] = construtor


def criar(
    nome: str,
    configuracao: Configuracao,
    aleatorio: random.Random | None = None,
) -> EscalonadorBase:
    """
    Cria e devolve uma instância nova do escalonador pedido.

    Se ``aleatorio`` não for fornecido, cria um ``random.Random()``
    não-determinístico (comportamento padrão em produção).

    Levanta ``ValueError`` com mensagem clara se o nome não estiver
    registrado, listando os algoritmos disponíveis.
    """
    if nome not in _registro:
        disponiveis = ", ".join(sorted(_registro)) or "(nenhum registrado)"
        raise ValueError(
            f"Algoritmo '{nome}' não encontrado. "
            f"Algoritmos disponíveis: {disponiveis}"
        )

    if aleatorio is None:
        aleatorio = random.Random()

    return _registro[nome](configuracao, aleatorio)


def listar_algoritmos() -> list[str]:
    """
    Devolve os nomes de todos os algoritmos registrados.

    Útil para a CLI rodar "todos os algoritmos" e para exibir as
    opções válidas ao usuário. A ordem segue a ordem de registro.
    """
    return list(_registro)
