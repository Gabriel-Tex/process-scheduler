import random

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.schedulers.factory import criar, listar_algoritmos
from src.scheduler.schedulers.fcfs import FCFS
from src.scheduler.schedulers.priority import (
    PrioridadeCooperativa,
    PrioridadePreemptiva,
)
from src.scheduler.schedulers.sjf import SJF
from src.scheduler.schedulers.srtf import SRTF


def test_algoritmos_do_epico_2_estao_registrados() -> None:
    algoritmos_esperados = {"fcfs", "sjf", "srtf", "prioc", "priop"}

    assert algoritmos_esperados.issubset(listar_algoritmos())


def test_fcfs_escolhe_menor_instante_de_criacao() -> None:
    processo_recente = Processo("P1", 4, 3, 1)
    processo_antigo = Processo("P2", 1, 5, 1)
    escalonador = FCFS(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_recente, 4)
    escalonador.ao_chegar(processo_antigo, 4)

    assert escalonador.selecionar_proximo(4, None) is processo_antigo


def test_fcfs_mantem_processo_em_execucao() -> None:
    processo_atual = Processo("P1", 5, 8, 1)
    processo_novo = Processo("P2", 0, 1, 1)
    escalonador = FCFS(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_atual, 5)
    escalonador.ao_chegar(processo_novo, 6)

    assert escalonador.selecionar_proximo(6, processo_atual) is processo_atual


def test_fcfs_desempata_instante_igual_por_menor_tempo_restante() -> None:
    processo_longo = Processo("P1", 0, 6, 1)
    processo_curto = Processo("P2", 0, 2, 1)
    escalonador = FCFS(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_longo, 0)
    escalonador.ao_chegar(processo_curto, 0)

    assert escalonador.selecionar_proximo(0, None) is processo_curto


def test_fcfs_desempate_absoluto_usa_gerador_injetado() -> None:
    primeiro = Processo("P1", 0, 3, 1)
    segundo = Processo("P2", 0, 3, 1)
    semente = 42
    escalonador = FCFS(Configuracao(), random.Random(semente))
    escalonador.ao_chegar(primeiro, 0)
    escalonador.ao_chegar(segundo, 0)

    esperado = random.Random(semente).choice([primeiro, segundo])
    assert escalonador.selecionar_proximo(0, None) is esperado


def test_fcfs_registrado_na_fabrica() -> None:
    assert "fcfs" in listar_algoritmos()
    assert isinstance(criar("fcfs", Configuracao(), random.Random(1)), FCFS)


def test_sjf_escolhe_menor_duracao_original() -> None:
    processo_longo = Processo("P1", 0, 6, 1)
    processo_curto = Processo("P2", 0, 2, 1)
    escalonador = SJF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_longo, 0)
    escalonador.ao_chegar(processo_curto, 0)

    assert escalonador.selecionar_proximo(0, None) is processo_curto


def test_sjf_mantem_processo_em_execucao_apesar_de_chegada_curta() -> None:
    processo_atual = Processo("P1", 0, 8, 1)
    processo_curto = Processo("P2", 1, 1, 1)
    escalonador = SJF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_curto, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_sjf_usa_duracao_original_e_nao_tempo_restante() -> None:
    processo_parcial = Processo("P1", 0, 5, 1)
    processo_parcial.tempo_restante = 1
    processo_curto = Processo("P2", 1, 3, 1)
    escalonador = SJF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_parcial, 2)
    escalonador.ao_chegar(processo_curto, 2)

    assert escalonador.selecionar_proximo(2, None) is processo_curto


def test_sjf_registrado_na_fabrica() -> None:
    assert "sjf" in listar_algoritmos()
    assert isinstance(criar("sjf", Configuracao(), random.Random(1)), SJF)


def test_prioc_escolhe_maior_prioridade_numerica() -> None:
    processo_prioridade_baixa = Processo("P1", 0, 3, 2)
    processo_prioridade_alta = Processo("P2", 0, 3, 9)
    escalonador = PrioridadeCooperativa(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_prioridade_baixa, 0)
    escalonador.ao_chegar(processo_prioridade_alta, 0)

    assert escalonador.selecionar_proximo(0, None) is processo_prioridade_alta


def test_prioc_nao_preempta_processo_em_execucao() -> None:
    processo_atual = Processo("P1", 0, 8, 1)
    processo_prioritario = Processo("P2", 1, 2, 10)
    escalonador = PrioridadeCooperativa(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_prioritario, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_prioc_desempata_prioridade_igual_por_menor_tempo_restante() -> None:
    processo_longo = Processo("P1", 0, 6, 5)
    processo_curto = Processo("P2", 0, 2, 5)
    escalonador = PrioridadeCooperativa(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_longo, 0)
    escalonador.ao_chegar(processo_curto, 0)

    assert escalonador.selecionar_proximo(0, None) is processo_curto


def test_prioc_registrado_na_fabrica() -> None:
    assert "prioc" in listar_algoritmos()
    assert isinstance(
        criar("prioc", Configuracao(), random.Random(1)), PrioridadeCooperativa
    )


def test_priop_preempta_quando_chega_prioridade_maior() -> None:
    processo_atual = Processo("P1", 0, 8, 3)
    processo_prioritario = Processo("P2", 1, 2, 8)
    escalonador = PrioridadePreemptiva(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_prioritario, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_prioritario


def test_priop_mantem_processo_diante_de_prioridade_menor() -> None:
    processo_atual = Processo("P1", 0, 8, 8)
    processo_menos_prioritario = Processo("P2", 1, 2, 3)
    escalonador = PrioridadePreemptiva(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_menos_prioritario, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_priop_empate_mantem_mesma_instancia_em_execucao() -> None:
    processo_atual = Processo("P1", 0, 8, 5)
    processo_recente = Processo("P2", 1, 2, 5)
    escalonador = PrioridadePreemptiva(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_recente, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_priop_com_cpu_ociosa_escolhe_maior_prioridade() -> None:
    processo_prioridade_baixa = Processo("P1", 0, 2, 3)
    processo_prioridade_alta = Processo("P2", 0, 8, 9)
    escalonador = PrioridadePreemptiva(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_prioridade_baixa, 0)
    escalonador.ao_chegar(processo_prioridade_alta, 0)

    assert escalonador.selecionar_proximo(0, None) is processo_prioridade_alta


def test_priop_registrado_na_fabrica() -> None:
    assert "priop" in listar_algoritmos()
    assert isinstance(
        criar("priop", Configuracao(), random.Random(1)), PrioridadePreemptiva
    )


def test_srtf_preempta_quando_chega_menor_tempo_restante() -> None:
    processo_atual = Processo("P1", 0, 8, 1)
    processo_curto = Processo("P2", 1, 2, 1)
    escalonador = SRTF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_curto, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_curto


def test_srtf_mantem_processo_atual_diante_de_maior_tempo_restante() -> None:
    processo_atual = Processo("P1", 0, 3, 1)
    processo_longo = Processo("P2", 1, 6, 1)
    escalonador = SRTF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_longo, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_srtf_empate_mantem_mesma_instancia_em_execucao() -> None:
    processo_atual = Processo("P1", 0, 4, 1)
    processo_recente = Processo("P2", 1, 4, 1)
    escalonador = SRTF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_recente, 1)

    assert escalonador.selecionar_proximo(1, processo_atual) is processo_atual


def test_srtf_usa_tempo_restante_atual() -> None:
    processo_quase_finalizado = Processo("P1", 0, 9, 1)
    processo_quase_finalizado.tempo_restante = 2
    processo_recente = Processo("P2", 1, 3, 1)
    escalonador = SRTF(Configuracao(), random.Random(1))
    escalonador.ao_chegar(processo_recente, 1)

    assert (
        escalonador.selecionar_proximo(1, processo_quase_finalizado)
        is processo_quase_finalizado
    )


def test_srtf_registrado_na_fabrica() -> None:
    assert "srtf" in listar_algoritmos()
    assert isinstance(criar("srtf", Configuracao(), random.Random(1)), SRTF)