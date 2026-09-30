"""Motor discreto: chegada -> seleção -> registro -> execução -> hook.

Não conhece Round-Robin nem qualquer algoritmo concreto. A política escolhe
quem executa; o motor avança o relógio e reúne resultados, segundo a segundo.
"""
from collections import defaultdict

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo, StatusProcesso
from src.scheduler.schedulers.base import EscalonadorBase
from .diagram import DiagramaTempo
from .result import ResultadoSimulacao


class MotorSimulacao:
    def executar(
        self, processos: list[Processo], escalonador: EscalonadorBase,
        config: Configuracao,
    ) -> ResultadoSimulacao:
        if not processos:
            raise ValueError("Adicione pelo menos um processo.")
        if len({p.id for p in processos}) != len(processos):
            raise ValueError("Os IDs dos processos devem ser únicos.")
        if config.quantum <= 0 or config.aging <= 0:
            raise ValueError("Quantum e aging devem ser positivos.")
        if any(p.tempo_restante != p.tempo_processamento or p.instante_inicio is not None
               for p in processos):
            raise ValueError("Cada execução precisa de processos novos.")

        chegadas = defaultdict(list)
        for p in processos:
            chegadas[p.instante_criacao].append(p)
        diagrama = DiagramaTempo([p.id for p in processos])
        registros = []
        atual = None
        tempo = 0
        concluidos = 0
        trocas = 0

        while concluidos < len(processos):
            # Chegadas entram antes de reenfileirar quem esgotou seu quantum.
            for p in chegadas.get(tempo, ()):
                p.status = StatusProcesso.PRONTO
                escalonador.ao_chegar(p, tempo)

            anterior = atual
            atual = escalonador.selecionar_proximo(tempo, anterior)
            presentes = frozenset(p.id for p in processos
                                 if p.instante_criacao <= tempo and p.tempo_restante > 0)
            if atual is None and presentes:
                raise RuntimeError("O escalonador deixou a CPU ociosa com processos prontos.")
            if atual is not None and (not any(atual is p for p in processos)
                                      or atual.id not in presentes):
                raise RuntimeError("O escalonador escolheu um processo que não está pronto.")

            if anterior is not None and anterior is not atual and anterior.tempo_restante > 0:
                anterior.status = StatusProcesso.PRONTO
            # Só transições diretas entre processos diferentes contam como troca.
            if anterior is not None and atual is not None and anterior is not atual:
                trocas += 1

            pid = atual.id if atual is not None else None
            registros.append((pid, presentes))
            diagrama.registrar_tick(pid, presentes)

            if atual is not None:
                atual.status = StatusProcesso.EXECUTANDO
                if atual.instante_inicio is None:
                    atual.instante_inicio = tempo
                atual.executar_um_tick()
                if atual.tempo_restante == 0:
                    atual.instante_termino = tempo + 1
                    atual.status = StatusProcesso.FINALIZADO
                    concluidos += 1

            # Mesmo quem terminou neste tick deve fechar sua fatia no hook.
            escalonador.ao_finalizar_tick(tempo, atual)
            tempo += 1

        vidas = [p.instante_termino - p.instante_criacao for p in processos]
        esperas = tuple((p.id, vida - p.tempo_processamento)
                        for p, vida in zip(processos, vidas))
        return ResultadoSimulacao(
            nome_algoritmo=getattr(escalonador, "nome", type(escalonador).__name__),
            tt_medio=sum(vidas) / len(processos),
            tw_medio=sum(espera for _, espera in esperas) / len(processos),
            trocas_contexto=trocas,
            diagrama=diagrama.renderizar(),
            registros=tuple(registros),
            esperas=esperas,
        )
