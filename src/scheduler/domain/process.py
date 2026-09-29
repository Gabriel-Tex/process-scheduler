"""
Entidades de domínio: Processo e StatusProcesso. Camada mais interna do projeto.
"""

from __future__ import annotations 
from dataclasses import dataclass, field
from enum import Enum, auto


class StatusProcesso(Enum):
    """
    Status de um processo

    NOVO: criado, mas instante_criacao ainda não foi alcançado
    PRONTO: na fila de prontos, aguardando CPU
    EXECUTANDO: ocupando a CPU neste tick
    FINALIZADO: tempo_restante chegou a zero; processo concluído
    """

    NOVO = auto()
    PRONTO = auto()
    EXECUTANDO = auto()
    FINALIZADO = auto()


@dataclass
class Processo:
    """
    Representa um processo durante toda a simulação.

    Campos de entrada:
        id, instante_criacao, tempo_processamento, prioridade_estatica.

    Campos calculados:
        tempo_restante, prioridade_dinamica, status,
        instante_inicio, instante_termino.
    """

    # CAMPOS DE ENTRADA
    id: str
    instante_criacao: int 
    tempo_processamento: int 
    prioridade_estatica: int 

    #  CAMPOS CALCULADOS
    tempo_restante: int = field(init=False)
    prioridade_dinamica: int = field(init=False)
    status: StatusProcesso = field(init=False, default=StatusProcesso.NOVO)
    instante_inicio: int | None = field(init=False, default=None)
    instante_termino: int | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Valida valores e inicializa campos a serem calculados."""
        if self.instante_criacao < 0:
            raise ValueError(
                f"Processo {self.id}: instante_criacao deve ser >= 0, "
                f"recebeu {self.instante_criacao}"
            )
        if self.tempo_processamento <= 0:
            raise ValueError(
                f"Processo {self.id}: tempo_processamento deve ser > 0, "
                f"recebeu {self.tempo_processamento}"
            )
        if self.prioridade_estatica < 0:
            raise ValueError(
                f"Processo {self.id}: prioridade_estatica deve ser >= 0, "
                f"recebeu {self.prioridade_estatica}"
            )

        # tempo restante começa como tempo de processamento e prioridade dinânica como prioridade estática
        self.tempo_restante = self.tempo_processamento
        self.prioridade_dinamica = self.prioridade_estatica


    def consumir_segundo(self) -> None:
        """
        Consome 1 unidade de CPU do processo.

        Decrementa tempo_restante e, se chegar a zero, marca o processo
        como FINALIZADO.
         
        Quem decide quando chamar este método é o motor de
        simulação, e quem decide qual processo deve executar é o
        escalonador.
        """
        if self.tempo_restante <= 0:
            raise RuntimeError(
                f"Processo {self.id}: tentativa de consumir um segundo com "
                f"tempo_restante={self.tempo_restante}"
            )

        self.tempo_restante -= 1

        if self.tempo_restante == 0:
            self.status = StatusProcesso.FINALIZADO

    @property 
    def finalizado(self) -> bool:
        """
        Atalho para checar se o processo já terminou. Os algoritmos
        e o motor podem usar ``if processo.finalizado`` diretamente.
        """
        return self.status == StatusProcesso.FINALIZADO
