"""Oráculos pequenos, calculados manualmente, para a execução completa."""
import random
import unittest

from src.scheduler.domain.process import Processo, StatusProcesso
from src.scheduler.domain.configuration import Configuracao
from src.scheduler.schedulers.base import EscalonadorBase
from src.scheduler.schedulers.factory import criar
from src.scheduler.simulator.engine import MotorSimulacao
from src.scheduler.gui.controller import ControladorGUI
from src.scheduler.gui.services import ServicoReal


class MotorTests(unittest.TestCase):
    def simular(self, dados, quantum=2, nome="rr"):
        processos = [Processo(f"P{i}", *linha) for i, linha in enumerate(dados, 1)]
        config = Configuracao(quantum, 1)
        resultado = MotorSimulacao().executar(processos, criar(nome, config, random.Random(0)), config)
        return processos, resultado

    def test_rr_exemplo_pdf_e_espera_individual(self):
        ps, r = self.simular([(0, 5, 2), (0, 2, 3), (1, 4, 1), (3, 3, 4)])
        self.assertEqual([pid for pid, _ in r.registros],
                         ["P1", "P1", "P2", "P2", "P3", "P3", "P1",
                          "P1", "P4", "P4", "P3", "P3", "P1", "P4"])
        self.assertEqual(r.esperas, (("P1", 8), ("P2", 2), ("P3", 7), ("P4", 8)))
        self.assertEqual((r.tt_medio, r.tw_medio, r.trocas_contexto), (9.75, 6.25, 7))
        self.assertEqual([p.instante_inicio for p in ps], [0, 2, 4, 8])
        self.assertEqual([p.instante_termino for p in ps], [13, 4, 12, 14])
        self.assertTrue(all(p.status is StatusProcesso.FINALIZADO for p in ps))
        for pid, espera in r.esperas:
            contada = sum(pid in presentes and executando != pid
                          for executando, presentes in r.registros)
            self.assertEqual(espera, contada)

    def test_dados_cadastrados_nao_sao_demo(self):
        c = ControladorGUI(ServicoReal())
        r = c.executar("2 4 1", "2", "1", ["rr"])[0]
        self.assertEqual(r.ids_processos, ("P1",))
        self.assertEqual([t.executando for t in r.registros], [None, None] + ["P1"] * 4)
        self.assertEqual(r.esperas, (("P1", 0),))
        self.assertEqual((r.tt_medio, r.tw_medio), (4, 0))
        self.assertEqual(r.nome_algoritmo, "Round-Robin")

    def test_quantum_um_e_invariantes(self):
        ps, r = self.simular([(0, 2, 1), (0, 2, 1)], quantum=1)
        self.assertEqual([pid for pid, _ in r.registros], ["P1", "P2", "P1", "P2"])
        self.assertEqual(r.esperas, (("P1", 1), ("P2", 2)))
        self.assertEqual(r.trocas_contexto, 3)

    def test_termino_antecipado_reinicia_quantum(self):
        _, r = self.simular([(0, 1, 1), (0, 4, 1), (0, 1, 1)], quantum=3)
        self.assertEqual([pid for pid, _ in r.registros],
                         ["P1", "P2", "P2", "P2", "P3", "P2"])
        self.assertEqual(r.esperas, (("P1", 0), ("P2", 2), ("P3", 4)))

    def test_chegada_fronteira_e_registro_ultimo_tick(self):
        _, r = self.simular([(0, 3, 1), (2, 1, 1)])
        self.assertEqual([pid for pid, _ in r.registros], ["P1", "P1", "P2", "P1"])
        self.assertEqual(r.registros[2][1], frozenset({"P1", "P2"}))
        self.assertEqual(r.registros[3][1], frozenset({"P1"}))

    def test_ociosidade_e_entrada_fora_de_ordem(self):
        _, r = self.simular([(4, 1, 1), (1, 1, 1)])
        self.assertEqual([pid for pid, _ in r.registros], [None, "P2", None, None, "P1"])
        self.assertEqual(r.esperas, (("P1", 0), ("P2", 0)))
        self.assertEqual(r.trocas_contexto, 0)

    def test_envelhecimento_sem_interrupcao_da_fatia(self):
        _, r = self.simular([(0, 3, 1), (1, 1, 100)], nome="rr_prio_aging")
        self.assertEqual([pid for pid, _ in r.registros], ["P1", "P1", "P2", "P1"])
        self.assertEqual(r.esperas, (("P1", 1), ("P2", 1)))

    def test_duas_execucoes_independentes(self):
        c = ControladorGUI(ServicoReal())
        a = c.executar("0 2 1\n0 3 2", "2", "1", ["rr", "rr_prio_aging"])
        b = c.executar("0 2 1\n0 3 2", "2", "1", ["rr", "rr_prio_aging"])
        self.assertEqual(a, b)
        self.assertEqual(len(a), 2)

    def test_aceita_outra_politica_sem_conhecer_sua_classe(self):
        class Cooperativo(EscalonadorBase):
            def __init__(self):
                self.fila = []
            def ao_chegar(self, processo, tempo):
                self.fila.append(processo)
            def selecionar_proximo(self, tempo, atual):
                if atual and atual.tempo_restante > 0:
                    return atual
                return self.fila.pop(0) if self.fila else None
        ps = [Processo("A", 0, 2, 1), Processo("B", 1, 1, 1)]
        r = MotorSimulacao().executar(ps, Cooperativo(), Configuracao())
        self.assertEqual([pid for pid, _ in r.registros], ["A", "A", "B"])
        self.assertEqual(r.esperas, (("A", 0), ("B", 1)))

    def test_motor_rejeita_entrada_vazia_ou_reutilizada(self):
        config = Configuracao()
        for ps in ([], [Processo("A", 0, 1, 1), Processo("A", 0, 1, 1)]):
            with self.assertRaises(ValueError):
                MotorSimulacao().executar(ps, criar("rr", config), config)
        ps, _ = self.simular([(0, 2, 1)])
        with self.assertRaises(ValueError):
            MotorSimulacao().executar(ps, criar("rr", config), config)
