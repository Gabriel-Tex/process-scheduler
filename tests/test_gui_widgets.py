"""Verificações de integração com Tk real. Exigem sessão gráfica disponível."""
import unittest
from dataclasses import replace
from unittest.mock import patch

from src.scheduler.gui.app_gui import AppGUI
from src.scheduler.gui.services import ServicoDemonstrativo
from src.scheduler.gui.widgets.input_widget import EXEMPLO


class JanelaTests(unittest.TestCase):
    def setUp(self):
        self.app = AppGUI()
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        self.app.fechar()

    def test_abre_sem_motor_e_demo_identificada(self):
        self.assertIn("disabled", self.app.botao_executar.state())
        self.app.demonstrar()
        self.app.update()
        self.assertIn("DEMONSTRAÇÃO", self.app.aviso.get())
        self.assertEqual(len(self.app.resultado.tabela.get_children()), 1)
        self.assertEqual(self.app.gantt.indice, 0)

    def test_entrada_exemplo_edicao_remocao_ids(self):
        e = self.app.entrada
        self.assertTrue(e.carregar_texto(EXEMPLO))
        item = e.tabela.get_children()[0]
        e.tabela.selection_set(item)
        self.app.update()
        for var, valor in zip(e.campos, ("0", "8", "2")):
            var.set(valor)
        e.editar()
        self.assertEqual(e.obter_texto().splitlines()[0], "0 8 2")
        e.remover()
        self.assertEqual(e.tabela.item(e.tabela.get_children()[0], "values")[0], "P1")

    def test_entrada_invalida_preserva_tabela(self):
        e = self.app.entrada
        e.carregar_texto(EXEMPLO)
        anterior = e.obter_texto()
        with patch("src.scheduler.gui.widgets.input_widget.messagebox.showerror") as erro:
            self.assertFalse(e.carregar_texto("0 banana 1"))
            erro.assert_called_once()
        self.assertEqual(e.obter_texto(), anterior)

    def test_animacao_pausa_reinicio_e_troca_cancelam_callback(self):
        g = self.app.gantt
        self.app.demonstrar()
        self.app.update()
        g.play()
        self.assertEqual(g.indice, 1)
        self.assertIsNotNone(g._agendamento)
        g.pause()
        self.assertIsNone(g._agendamento)
        g.avancar_tick()
        self.assertEqual(g.indice, 2)
        g.play()
        g.reiniciar()
        self.assertIsNone(g._agendamento)
        self.assertEqual(g.indice, 0)
        g.play()
        g.carregar(ServicoDemonstrativo.carregar()[0])
        self.assertIsNone(g._agendamento)

    def test_texto_sem_registros_desabilita_animacao(self):
        r = replace(ServicoDemonstrativo.carregar()[0], registros=None)
        self.app.gantt.carregar(r)
        self.assertTrue(all("disabled" in b.state() for b in self.app.gantt.botoes))
        self.assertIn("tempo", self.app.gantt.texto.get("1.0", "end"))

    def test_redimensionar_e_rolar_diagrama_longo(self):
        self.app.deiconify()
        self.app.geometry("1000x900")
        original = ServicoDemonstrativo.carregar()[0]
        self.app.gantt.carregar(replace(original, registros=original.registros * 20))
        self.app.update()
        g = self.app.gantt
        self.assertGreaterEqual(g.canvas.winfo_height(), 90)
        g._rolar_x("moveto", 0.5)
        self.assertGreater(g.canvas.xview()[0], 0.1)
        g.reiniciar()
        self.assertAlmostEqual(g.canvas.xview()[0], 0.0)

    def test_importacao_config_invalida_preserva_valores(self):
        from io import StringIO
        cfg = self.app.config
        with patch("src.scheduler.gui.widgets.config_widget.filedialog.askopenfilename",
                   return_value="config.txt"), \
             patch("builtins.open", return_value=StringIO("quantum:0\naging:1")), \
             patch("src.scheduler.gui.widgets.config_widget.messagebox.showerror") as erro:
            cfg.importar()
            erro.assert_called_once()
        self.assertEqual((cfg.quantum.get(), cfg.aging.get()), ("2", "1"))

    def test_registro_real_simulado_atualiza_widgets(self):
        class Fake:
            def listar_algoritmos(self):
                return ["rr"]

            def executar(self, processos, config, algoritmos):
                return [replace(ServicoDemonstrativo.carregar()[0], nome_algoritmo="RR de teste")]

        self.app.fechar()
        self.app = AppGUI(Fake())
        self.app.withdraw()
        self.app.entrada.carregar_texto(EXEMPLO)
        self.app.executar()
        # Aguarda eventos Tk com limite; não depende de sleep na interface.
        self.app.after(3000, self.app.quit)
        def verificar():
            if not self.app._ocupado:
                self.app.quit()
            else:
                self.app.after(10, verificar)
        self.app.after(10, verificar)
        self.app.mainloop()
        self.assertFalse(self.app._ocupado)
        self.assertFalse(self.app._demo)
        self.assertEqual(self.app.resultado.resultados[0].nome_algoritmo, "RR de teste")
        self.assertIn("concluída", self.app.aviso.get())
