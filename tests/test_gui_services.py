import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.scheduler.domain.configuration import Configuracao
from src.scheduler.domain.process import Processo
from src.scheduler.gui.controller import ControladorGUI
from src.scheduler.gui.services import ServicoReal, ServicoDemonstrativo, adaptar_resultado


class ServicoFalso:
    def __init__(self):
        self.chamadas = []

    def listar_algoritmos(self):
        return ["rr", "rr_prio_aging"]

    def executar(self, processos, config, algoritmos):
        self.chamadas.append((processos, config, algoritmos))
        return ServicoDemonstrativo.carregar()


class ControladorTests(unittest.TestCase):
    def setUp(self):
        self.servico = ServicoFalso()
        self.c = ControladorGUI(self.servico)

    def test_valida_e_encaminha_selecao(self):
        resultados = self.c.executar("3 2 1\n0 1 4", "2", "1", ["rr"])
        ps, cfg, algs = self.servico.chamadas[0]
        self.assertEqual([(p.id, p.instante_criacao) for p in ps], [("P1", 3), ("P2", 0)])
        self.assertEqual((cfg.quantum, cfg.aging), (2, 1))
        self.assertEqual(algs, ["rr"])
        self.assertIs(self.c.resultados, resultados)

    def test_dados_invalidos_nao_chamam_servico(self):
        casos = [("", "2", "1", ["rr"]), ("0 0 1", "2", "1", ["rr"]),
                 ("0 1 1", "0", "1", ["rr"]), ("0 1 1", "2", "0", ["rr"]),
                 ("0 1 1", "2", "1", []), ("0 1 1", "2", "1", ["inexistente"])]
        for args in casos:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.c.executar(*args)
        self.assertEqual(self.servico.chamadas, [])

    def test_erro_preserva_resultado_anterior(self):
        anteriores = self.c.executar("0 1 1", "2", "1", ["rr"])
        with patch.object(self.servico, "executar", side_effect=RuntimeError("Falha")):
            with self.assertRaises(RuntimeError):
                self.c.executar("0 1 1", "2", "1", ["rr"])
        self.assertIs(self.c.resultados, anteriores)

    def test_validacao_informa_linha(self):
        with self.assertRaisesRegex(ValueError, "Linha 2"):
            self.c.validar_processos("0 1 1\n1 abc 2")

    def test_preempcao_desativada_rejeita_rr_sem_mudar_suas_regras(self):
        with self.assertRaisesRegex(ValueError, "cooperativo"):
            self.c.executar("0 2 1", "2", "1", ["rr"], permitir_preempcao=False)
        self.assertFalse(self.servico.chamadas)

    def test_demonstracao_independente_e_consistente(self):
        resultado = ServicoDemonstrativo.carregar()[0]
        self.assertEqual(len(resultado.registros), 14)
        self.assertEqual([sum(t.executando == p for t in resultado.registros)
                          for p in resultado.ids_processos], [5, 2, 4, 3])
        self.assertEqual(sum(a.executando != b.executando
                             for a, b in zip(resultado.registros, resultado.registros[1:])),
                         resultado.trocas_contexto)
        self.assertEqual((resultado.tt_medio, resultado.tw_medio), (9.75, 6.25))


class AdaptadorTests(unittest.TestCase):
    def resultado(self, **extra):
        return SimpleNamespace(nome_algoritmo="RR", tt_medio=2.0, tw_medio=1.0,
                               trocas_contexto=0, diagrama="texto", **extra)

    def test_aceita_resultado_apenas_textual(self):
        r = adaptar_resultado(self.resultado(), ("P1",))
        self.assertIsNone(r.registros)
        self.assertEqual(r.diagrama, "texto")

    def test_registros_sao_copiados_para_estrutura_imutavel(self):
        presentes = {"P1"}
        r = adaptar_resultado(self.resultado(registros=[("P1", presentes)]), ("P1",))
        presentes.clear()
        self.assertEqual(r.registros[0].presentes, frozenset({"P1"}))

    def test_motor_ausente_tem_mensagem_clara(self):
        with patch.object(ServicoReal, "_classe_motor", return_value=None):
            s = ServicoReal()
            self.assertIn("épico 1", s.motivo_indisponivel())
            with self.assertRaises(RuntimeError):
                s.executar([], Configuracao(), ["rr"])

    def test_motor_recebe_instancias_frescas_e_adaptador_devolve_resultados(self):
        entradas = []
        resultado = self.resultado()

        class MotorFalso:
            def executar(self, processos, escalonador, config):
                entradas.append((processos, escalonador, config))
                processos[0].executar_um_tick()
                config.quantum = 999
                return resultado

        original = Processo("P1", 0, 3, 1)
        config = Configuracao(2, 1)
        with patch.object(ServicoReal, "_classe_motor", return_value=MotorFalso):
            rs = ServicoReal().executar([original], config, ["rr", "rr_prio_aging"])
        self.assertEqual(len(rs), 2)
        self.assertEqual(original.tempo_restante, 3)
        self.assertEqual(config.quantum, 2)
        self.assertIsNot(entradas[0][0][0], entradas[1][0][0])
        self.assertIsNot(entradas[0][1], entradas[1][1])
        self.assertEqual([it[0][0].tempo_restante for it in entradas], [2, 2])
