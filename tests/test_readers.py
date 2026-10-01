"""Contratos de entrada compartilhados com a GUI e a futura CLI."""
from io import StringIO
import unittest
from src.scheduler.io.input_reader import ler_processos
from src.scheduler.io.config_reader import ler_configuracao
from src.scheduler.simulator.diagram import DiagramaTempo


class LeitoresTests(unittest.TestCase):
    def test_espacos_linhas_vazias_e_ordem_original(self):
        ps = ler_processos(StringIO("\n 3  2\t1\n0 1 2\n"))
        self.assertEqual([(p.id, p.instante_criacao) for p in ps], [("P1", 3), ("P2", 0)])

    def test_erros_de_entrada_indicam_linha(self):
        for linha in ("0 1", "0 x 1", "-1 1 1", "0 0 1", "0 1 -1"):
            with self.subTest(linha=linha), self.assertRaisesRegex(ValueError, "Linha 2"):
                ler_processos(StringIO("0 1 1\n" + linha))

    def test_config_exige_chaves_unicas_conhecidas_e_positivas(self):
        for texto in ("quantum:2", "quantum:2\naging:1\naging:2",
                      "quantum:2\naging:1\nextra:1", "quantum:0\naging:1",
                      "quantum:2\naging:-1", "quantum:abc\naging:1"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                ler_configuracao(StringIO(texto))

    def test_config_aceita_comentarios_e_espacos(self):
        c = ler_configuracao(StringIO("# exemplo\n Quantum : 2\n\naging: 1\n"))
        self.assertEqual((c.quantum, c.aging), (2, 1))

    def test_diagrama_preserva_ausencia_espera_execucao_e_copia(self):
        d = DiagramaTempo(["P1", "P2", "P3"])
        self.assertEqual(len(d.renderizar().splitlines()), 1)
        presentes = {"P1", "P2"}
        d.registrar_tick("P1", presentes)
        presentes.clear()
        linha = d.renderizar().splitlines()[1]
        self.assertIn("##  --", linha)
        self.assertTrue(linha.endswith("    "))
