import unittest
from io import StringIO
from src.scheduler.io.output_writer import _formatar_numero, formatar_resultado, formatar_tabela_comparativa, escrever_resultados
from src.scheduler.simulator.result import ResultadoSimulacao
from src.scheduler.simulator.diagram import DiagramaTempo

class MockDiagrama(DiagramaTempo):
    def __init__(self, render_text):
        self.render_text = render_text
    def renderizar(self):
        return self.render_text

class WriterTests(unittest.TestCase):
    def test_w1_formatar_numero(self):
        self.assertEqual(_formatar_numero(8.0), "8,0")
        self.assertEqual(_formatar_numero(5.8), "5,8")
        self.assertEqual(_formatar_numero(9.75), "9,75")
        self.assertEqual(_formatar_numero(7.4), "7,4")
        self.assertEqual(_formatar_numero(0.0), "0,0")
        self.assertEqual(_formatar_numero(9.754), "9,75")

    def test_w2_w3_bloco_oraculo_pdf(self):
        r = ResultadoSimulacao(
            nome_algoritmo="rr",
            tt_medio=9.75,
            tw_medio=6.25,
            trocas_contexto=7,
            diagrama="tempo  P1 P2\n 0- 1  ##  --",
            registros=[],
            esperas=[],
           
        )
        bloco = formatar_resultado(r)
        self.assertIn("=== rr ===", bloco)
        self.assertIn("Tempo médio de vida (tt): 9,75", bloco)
        self.assertIn("Tempo médio de espera (tw): 6,25", bloco)
        self.assertIn("Número de trocas de contexto: 7", bloco)
        self.assertIn("tempo  P1 P2\n 0- 1  ##  --", bloco)

    def test_w4_tabela_comparativa(self):
        r1 = ResultadoSimulacao("fcfs", 7.4, 4.6, 4, "", [], [])
        r2 = ResultadoSimulacao("sjf", 5.8, 3.0, 4, "", [], [])
        # Adicionar campo tempo_total se testado, mas vamos verificar básico
        tab = formatar_tabela_comparativa([r1, r2])
        self.assertIn("Quadro comparativo", tab)
        self.assertIn("fcfs       7,4  4,6       4", tab)
        self.assertIn("sjf        5,8  3,0       4", tab)

    def test_w5_w6_w8_escrever_resultados(self):
        r1 = ResultadoSimulacao("fcfs", 7.4, 4.6, 4, "", [], [])
        r2 = ResultadoSimulacao("sjf", 5.8, 3.0, 4, "", [], [])
        
        saida1 = StringIO()
        escrever_resultados([r1], saida1)
        self.assertNotIn("Quadro comparativo", saida1.getvalue())
        
        saida2 = StringIO()
        escrever_resultados([r1, r2], saida2)
        self.assertIn("Quadro comparativo", saida2.getvalue())
        self.assertIn("=== fcfs ===", saida2.getvalue())

    def test_w7_lista_vazia(self):
        with self.assertRaises(ValueError):
            escrever_resultados([], StringIO())
        with self.assertRaises(ValueError):
            formatar_tabela_comparativa([])

if __name__ == '__main__':
    unittest.main()
