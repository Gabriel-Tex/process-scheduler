"""
Diagrama de tempo da simulação — apresentação textual "Gantt vertical".

Classe puramente de apresentação: acumula o estado de cada tick (quem
executou, quem estava presente) e renderiza o diagrama no formato de texto. 
Não sabe o que é um ``Processo``, não decide nada sobre escalonamento, 
não calcula métricas — trabalha apenas com ids (``str``) e conjuntos.

Regra das três células:
    ``##`` — o processo está executando naquele segundo.
    ``--`` — o processo já chegou e ainda não terminou, mas não está na CPU.
    ``  `` — o processo ainda não chegou ou já terminou (célula em branco).
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence


class DiagramaTempo:
    """
    Acumula o estado tick a tick e renderiza o diagrama de tempo.

    A ordem das colunas é fixada na criação (ids dos processos, na ordem
    de leitura da entrada). Cada chamada a ``registrar_tick`` adiciona uma
    linha ao diagrama; ``renderizar`` produz a string formatada completa.

    Este módulo não importa nada de ``dominio/``, ``escalonadores/``,
    ``io/``, ``cli/`` ou ``gui/`` — é a classe mais independente do
    projecto depois do próprio domínio.
    """

    def __init__(self, ids_processos: Sequence[str]) -> None:
        """
        Fixa a ordem das colunas do diagrama.

        Args:
            ids_processos: Lista de ids na ordem em que devem aparecer
                como colunas (tipicamente P1, P2, P3, …, na ordem de
                leitura da entrada).
        """
        self._ids: list[str] = list(ids_processos)
        # Cada entrada: (id_executando | None, frozenset dos ids presentes)
        self._ticks: list[tuple[str | None, frozenset[str]]] = []

    def registrar_tick(
        self,
        executando: str | None,
        presentes: Iterable[str],
    ) -> None:
        """
        Registra o estado de um segundo de simulação.

        Chamado uma vez por tick, em ordem crescente, começando no tick 0.
        O tempo é implícito pela ordem das chamadas — a primeira chamada é
        o tick 0, a segunda é o tick 1, etc.

        Args:
            executando: Id do processo que ocupa a CPU neste tick, ou
                ``None`` se a CPU está ociosa.
            presentes: Ids que já chegaram e ainda não terminaram neste
                tick. Pode ou não incluir ``executando`` — a renderização
                trata ``##`` para quem executa independentemente.
        """
        self._ticks.append((executando, frozenset(presentes)))

    def renderizar(self) -> str:
        """
        Devolve o diagrama completo formatado como texto.

        Produz cabeçalho + uma linha por tick registrado. Funciona mesmo
        com zero ticks (devolve apenas o cabeçalho). Não faz ``print`` —
        quem decide imprimir é a camada de apresentação (CLI/GUI).
        """
        if not self._ids:
            return ""

        # --- larguras de coluna ---
        # Largura da coluna de tempo: depende do maior rótulo de tempo.
        # Ex.: "0- 1" tem 4 chars, "99-100" tem 6. Calculamos pelo último tick.
        ultimo_tick = len(self._ticks)  # tick seguinte ao último registado
        if ultimo_tick == 0:
            # Sem ticks — usar largura mínima para o cabeçalho "tempo".
            largura_tempo = len("tempo")
        else:
            # O rótulo mais largo é o do último tick (maiores números).
            rotulo_ultimo = f"{ultimo_tick - 1}-{ultimo_tick}"
            largura_tempo = max(len("tempo"), len(rotulo_ultimo))

        # Cada coluna de processo tem largura fixa = max(2, len(id)).
        # 2 é o mínimo para caber "##" e "--".
        larguras_proc = [max(2, len(pid)) for pid in self._ids]

        # --- cabeçalho ---
        partes_cabecalho = [f"{'tempo':>{largura_tempo}}"]
        for pid, larg in zip(self._ids, larguras_proc):
            partes_cabecalho.append(f"{pid:>{larg}}")
        cabecalho = "  ".join(partes_cabecalho)

        # --- linhas de dados ---
        linhas: list[str] = [cabecalho]

        for i, (exec_id, conj_presentes) in enumerate(self._ticks):
            # Rótulo de tempo: "0- 1", "1- 2", …, alinhado à direita.
            rotulo = f"{i}-{i + 1}"
            partes_linha = [f"{rotulo:>{largura_tempo}}"]

            for pid, larg in zip(self._ids, larguras_proc):
                # Regra das três células:
                #   ## — executando (tem prioridade sobre estar em presentes)
                #   -- — presente mas não executando
                #   (espaço) — ausente
                if pid == exec_id:
                    celula = "##"
                elif pid in conj_presentes:
                    celula = "--"
                else:
                    celula = "  "
                partes_linha.append(f"{celula:>{larg}}")

            linhas.append("  ".join(partes_linha))

        return "\n".join(linhas)
