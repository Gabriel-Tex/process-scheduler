import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.key_based import EscalonadorPorChave


def _chave_instante_criacao(processo: Processo) -> int:
    return processo.instante_criacao


def _chave_prioridade_dinamica(processo: Processo) -> int:
    return processo.prioridade_dinamica


def _criar_escalonador(preemptivo: bool) -> EscalonadorPorChave:
    return EscalonadorPorChave(
        Configuracao(),
        _chave_instante_criacao,
        preemptivo,
        random.Random(1),
    )


def test_nao_preemptivo_mantem_processo_em_execucao() -> None:
    em_execucao = Processo("P1", 5, 8, 1)
    candidato = Processo("P2", 1, 2, 1)
    escalonador = _criar_escalonador(preemptivo=False)
    escalonador.ao_chegar(candidato, 5)

    assert escalonador.selecionar_proximo(5, em_execucao) is em_execucao


def test_preemptivo_escolhe_candidato_com_chave_menor() -> None:
    em_execucao = Processo("P1", 5, 8, 1)
    candidato = Processo("P2", 1, 2, 1)
    escalonador = _criar_escalonador(preemptivo=True)
    escalonador.ao_chegar(candidato, 5)

    assert escalonador.selecionar_proximo(5, em_execucao) is candidato


def test_preemptivo_mantem_processo_atual_em_empate_de_chave() -> None:
    em_execucao = Processo("P1", 3, 8, 1)
    candidato = Processo("P2", 3, 2, 1)
    escalonador = _criar_escalonador(preemptivo=True)
    escalonador.ao_chegar(candidato, 5)

    assert escalonador.selecionar_proximo(5, em_execucao) is em_execucao


def test_chave_dinamica_e_recalculada_a_cada_selecao() -> None:
    em_execucao = Processo("P1", 0, 8, 2)
    candidato = Processo("P2", 0, 2, 5)
    escalonador = EscalonadorPorChave(
        Configuracao(),
        _chave_prioridade_dinamica,
        preemptivo=True,
        aleatorio=random.Random(1),
    )
    escalonador.ao_chegar(candidato, 0)

    assert escalonador.selecionar_proximo(0, em_execucao) is em_execucao

    candidato.prioridade_dinamica = 1
    assert escalonador.selecionar_proximo(1, em_execucao) is candidato


def test_empate_de_chave_escolhe_menor_tempo_restante() -> None:
    processo_longo = Processo("P1", 3, 8, 1)
    processo_curto = Processo("P2", 3, 2, 1)
    escalonador = _criar_escalonador(preemptivo=False)
    escalonador.ao_chegar(processo_longo, 5)
    escalonador.ao_chegar(processo_curto, 5)

    assert escalonador.selecionar_proximo(5, None) is processo_curto


def test_sem_candidatos_retorna_none() -> None:
    escalonador = _criar_escalonador(preemptivo=False)

    assert escalonador.selecionar_proximo(0, None) is None