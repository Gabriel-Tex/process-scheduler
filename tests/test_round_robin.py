"""Cenários pequenos com sequências esperadas; este driver existe só nos testes."""
import random
import unittest
from src.scheduler.domain.process import Processo
from src.scheduler.domain.configuration import Configuracao
from src.scheduler.schedulers.round_robin import RoundRobin
from src.scheduler.schedulers.round_robin_aging import RoundRobinAging
from src.scheduler.schedulers import factory


def processo(pid, chegada=0, duracao=3, prioridade=1):
    return Processo(pid, chegada, duracao, prioridade)


def ticks(escalonador, processos, limite=100):
    atual = None
    sequencia = []
    for t in range(limite):
        for p in processos:
            if p.instante_criacao == t:
                escalonador.ao_chegar(p, t)
        atual = escalonador.selecionar_proximo(t, atual)
        sequencia.append(atual.id if atual else None)
        if atual:
            atual.executar_um_tick()
        # O hook recebe quem executou, inclusive se terminou neste tick.
        escalonador.ao_finalizar_tick(t, atual)
        if all(p.tempo_restante == 0 for p in processos):
            return sequencia
    raise AssertionError("O escalonador não terminou o cenário")


class RoundRobinTests(unittest.TestCase):
    def rr(self, quantum):
        return RoundRobin(Configuracao(quantum, 1), random.Random(0))

    def test_quantum_um(self):
        self.assertEqual(ticks(self.rr(1), [processo("A", duracao=2), processo("B", duracao=2)]),
                         ["A", "B", "A", "B"])

    def test_quantum_dois(self):
        self.assertEqual(ticks(self.rr(2), [processo("A"), processo("B")]),
                         ["A", "A", "B", "B", "A", "B"])

    def test_termino_antecipado_reinicia_fatia(self):
        self.assertEqual(ticks(self.rr(3), [processo("A", duracao=1),
                                          processo("B", duracao=4), processo("C", duracao=1)]),
                         ["A", "B", "B", "B", "C", "B"])

    def test_processo_unico(self):
        self.assertEqual(ticks(self.rr(2), [processo("A", duracao=5)]), ["A"] * 5)

    def test_chegada_nao_interrompe_fatia(self):
        self.assertEqual(ticks(self.rr(2), [processo("A"), processo("B", 1, 1)]),
                         ["A", "A", "B", "A"])

    def test_chegada_na_fronteira_precede_reenfileirado(self):
        self.assertEqual(ticks(self.rr(2), [processo("A"), processo("B", 2, 1)]),
                         ["A", "A", "B", "A"])

    def test_intervalo_ocioso_e_entrada_fora_de_ordem(self):
        self.assertEqual(ticks(self.rr(2), [processo("B", 4, 1), processo("A", 1, 1)]),
                         [None, "A", None, None, "B"])

    def test_prioridade_nao_influencia_rr(self):
        self.assertEqual(ticks(self.rr(1), [processo("A", duracao=1, prioridade=1),
                                          processo("B", duracao=1, prioridade=100)]), ["A", "B"])

    def test_quantum_invalido(self):
        with self.assertRaises(ValueError):
            self.rr(0)


class AgingTests(unittest.TestCase):
    def rr(self, quantum=2, aging=1, seed=0):
        return RoundRobinAging(Configuracao(quantum, aging), random.Random(seed))

    def test_prioridade_maior_chega_sem_preempcao(self):
        self.assertEqual(ticks(self.rr(), [processo("A"), processo("B", 1, 1, 100)]),
                         ["A", "A", "B", "A"])

    def test_envelhecimento_fronteiras(self):
        rr = self.rr(2, 3)
        a, b = processo("A", prioridade=10), processo("B")
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        atual = rr.selecionar_proximo(0, None) # fronteira: b ganha aging, a restaurado
        self.assertIs(atual, a)
        self.assertEqual(b.prioridade_dinamica, 4)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)
        self.assertEqual(b.prioridade_dinamica, 4)
        a.executar_um_tick()
        rr.ao_finalizar_tick(1, a)
        
        atual = rr.selecionar_proximo(2, a) # fronteira (esgotou quantum)
        self.assertEqual(b.prioridade_dinamica, 7)
        self.assertEqual(a.prioridade_dinamica, 10)

    def test_fatia_incompleta_envelhece(self):
        rr = self.rr(3, 2)
        a, b = processo("A", duracao=1, prioridade=10), processo("B")
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        self.assertIs(rr.selecionar_proximo(0, None), a)
        self.assertEqual(b.prioridade_dinamica, 3)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)
        self.assertIs(rr.selecionar_proximo(1, a), b)
        # fronteira de término antecipado (a duracao=1). b é escolhido, pd cai pra 1
        self.assertEqual(b.prioridade_dinamica, 1)

    def test_quantum_completo_com_termino_envelhece(self):
        rr = self.rr(1, 2)
        a, b = processo("A", duracao=1, prioridade=10), processo("B")
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        rr.selecionar_proximo(0, None)
        self.assertEqual(b.prioridade_dinamica, 3)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)

    def test_chegada_na_fronteira_nao_recebe_aging_retroativo(self):
        rr = self.rr(1, 5)
        a = processo("A", prioridade=10)
        rr.ao_chegar(a, 0)
        rr.selecionar_proximo(0, None)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)
        b = processo("B", 1, 2, 1)
        rr.ao_chegar(b, 1)
        self.assertEqual(b.prioridade_dinamica, 1)

    def test_prioridade_restaurada_ao_selecionar(self):
        rr = self.rr(1, 3)
        a, b = processo("A", prioridade=3), processo("B", prioridade=1)
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        rr.selecionar_proximo(0, None)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)
        self.assertEqual(b.prioridade_dinamica, 4)
        self.assertIs(rr.selecionar_proximo(1, a), b)
        self.assertEqual(b.prioridade_dinamica, 1)

    def test_empate_prefere_atual(self):
        rr = self.rr(1, 1)
        a, b = processo("A", prioridade=2), processo("B", duracao=1, prioridade=1)
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        self.assertIs(rr.selecionar_proximo(0, None), a)
        a.executar_um_tick()
        rr.ao_finalizar_tick(0, a)
        self.assertIs(rr.selecionar_proximo(1, a), a)

    def test_empate_prefere_menor_restante(self):
        rr = self.rr()
        a, b = processo("A", duracao=5), processo("B", duracao=1)
        rr.ao_chegar(a, 0)
        rr.ao_chegar(b, 0)
        self.assertIs(rr.selecionar_proximo(0, None), b)

    def test_sorteio_reproduzivel(self):
        resultados = [ticks(self.rr(seed=17), [processo("A"), processo("B"), processo("C")])
                      for _ in range(2)]
        self.assertEqual(*resultados)

    def test_quantum_um_alterna_com_aging(self):
        self.assertEqual(ticks(self.rr(1), [processo("A", duracao=1, prioridade=2),
                                           processo("B", duracao=2)]), ["A", "B", "B"])

    def test_unico_e_ociosidade(self):
        self.assertEqual(ticks(self.rr(), [processo("A", 2, 5)]),
                         [None, None, "A", "A", "A", "A", "A"])

    def test_validacao(self):
        for q, a in ((0, 1), (1, 0), (-1, 1), (1, -1)):
            with self.subTest(q=q, a=a), self.assertRaises(ValueError):
                self.rr(q, a)

    def test_fabrica_disponibiliza_algoritmos(self):
        for _ in range(2):
            self.assertIn("rr", factory.listar_algoritmos())
            self.assertIn("rr_prio_aging", factory.listar_algoritmos())
        self.assertIsInstance(factory.criar("rr", Configuracao()), RoundRobin)
        self.assertIsInstance(factory.criar("rr_prio_aging", Configuracao()), RoundRobinAging)
