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
        self.app.update_idletasks()
        self.app.fechar()

    def test_abre_com_motor_e_demo_identificada(self):
        self.assertNotIn("disabled", self.app.botao_executar.state())
        self.app.demonstrar()
        self.app.update()
        self.assertIn("DEMONSTRAÇÃO", self.app.aviso.get())
        self.assertEqual(len(self.app.resultado.tabela.get_children()), 1)
        self.assertEqual(self.app.gantt.indice, 0)

    def test_ausencia_motor_ainda_tem_fallback(self):
        from src.scheduler.gui.services import ServicoReal
        self.app.fechar()
        with patch.object(ServicoReal, "_classe_motor", return_value=None):
            self.app = AppGUI()
        self.app.withdraw()
        self.assertIn("disabled", self.app.botao_executar.state())

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

    def test_voltar_pausa_e_nao_ultrapassa_inicio(self):
        self.app.demonstrar()
        self.app.update()
        g = self.app.gantt
        g.play()
        g.voltar_tick()
        self.app.update()
        self.assertEqual(g.indice, 0)
        self.assertIsNone(g._agendamento)
        self.assertFalse(g._tocando)
        g.voltar_tick()
        self.assertEqual(g.indice, 0)
        g.finalizar()
        g.voltar_tick()
        self.app.update()
        self.assertEqual(g.indice, 13)
        self.assertEqual(g._pintado_ate, 13)

    def test_aba_selecionada_cinza_com_fonte_maior(self):
        from tkinter import ttk, font
        estilo = ttk.Style(self.app)
        selecionada = estilo.lookup("Timeline.TNotebook.Tab", "background", ("selected",))
        normal = estilo.lookup("Timeline.TNotebook.Tab", "background")
        self.assertEqual(selecionada, "#cbd5e1")
        self.assertNotEqual(selecionada, normal)
        maior = font.Font(root=self.app, font=estilo.lookup("Timeline.TNotebook.Tab", "font", ("selected",)))
        menor = font.Font(root=self.app, font=estilo.lookup("Timeline.TNotebook.Tab", "font"))
        self.assertGreater(maior.actual("size"), menor.actual("size"))

    def test_sem_preempcao_exclui_rr_e_informa_pendencia(self):
        cfg = self.app.config
        cfg.permitir_preempcao.set(False)
        cfg._atualizar_lista()
        self.assertEqual(cfg.selecionados(), [])
        self.assertIn("disabled", self.app.botao_executar.state())
        self.assertIn("épico 2", self.app.disponibilidade.cget("text"))
        self.assertTrue(all("disabled" in e.state() for e in cfg._entradas_numericas))
        cfg.permitir_preempcao.set(True)
        cfg._atualizar_lista()
        self.assertIn("rr", cfg.selecionados())
        self.assertNotIn("disabled", self.app.botao_executar.state())

    def test_futuros_cooperativos_podem_ser_selecionados_sem_quantum(self):
        from src.scheduler.gui.widgets.config_widget import ConfigWidget
        cfg = ConfigWidget(self.app, ["fcfs", "sjf", "prioc", "srtf", "priop", "rr"])
        cfg.permitir_preempcao.set(False)
        cfg._atualizar_lista()
        self.assertEqual(cfg.selecionados(), ["fcfs", "sjf", "prioc"])
        cfg.quantum.set("não usado")
        self.assertEqual(cfg.valores_config(), ("2", "1"))
        cfg.destroy()

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

    def test_alternar_abas_preserva_posicao_e_reutiliza_canvas(self):
        self.app.deiconify()
        self.app.demonstrar()
        self.app.update()
        g = self.app.gantt
        g.avancar_tick()
        self.app.update()
        itens = g.canvas.find_all()
        for _ in range(4):
            g.abas.select(1)
            self.app.update()
            g.abas.select(0)
            self.app.update()
        self.assertEqual(g.indice, 1)
        self.assertEqual(g.canvas.find_all(), itens)
        g.finalizar()
        self.app.update()
        self.assertEqual(g.indice, 14)
        self.assertIsNone(g._agendamento)
        g.abas.select(1)
        self.app.update()
        g.abas.select(0)
        self.app.update()
        self.assertEqual(g.canvas.find_all(), itens)
        self.assertEqual(g.indice, 14)

    def test_canvas_oculto_nao_redesenha_e_retorna_no_tick_correto(self):
        self.app.deiconify()
        self.app.demonstrar()
        self.app.update()
        g = self.app.gantt
        g.abas.select(1)
        self.app.update()
        itens = g.canvas.find_all()
        g.avancar_tick()
        self.app.update()
        self.assertEqual(g.canvas.find_all(), itens)
        self.assertEqual(g._pintado_ate, 0)
        g.abas.select(0)
        self.app.update()
        self.assertEqual(g._pintado_ate, 1)

    def test_selecao_duplicada_nao_reinicia_reproducao(self):
        self.app.demonstrar()
        self.app.update()
        g = self.app.gantt
        g.avancar_tick()
        g.carregar(g.resultado)
        self.assertEqual(g.indice, 1)

    def test_executa_processos_da_tabela_e_mostra_espera_real(self):
        self.app.entrada.carregar_texto("0 3 1\n1 1 1")
        self.app.config.lista.selection_clear(0, "end")
        indice = self.app.config.algoritmos.index("rr")
        self.app.config.lista.selection_set(indice)
        self.app.executar()
        limite = self.app.after(3000, self.app.quit)
        def verificar():
            if not self.app._ocupado:
                self.app.quit()
            else:
                self.app.after(10, verificar)
        self.app.after(10, verificar)
        self.app.mainloop()
        self.app.after_cancel(limite)
        self.app.update()
        self.assertFalse(self.app._ocupado)
        self.assertFalse(self.app._demo)
        g = self.app.gantt
        self.assertEqual(g.resultado.ids_processos, ("P1", "P2"))
        self.assertEqual([t.executando for t in g.resultado.registros], ["P1", "P1", "P2", "P1"])
        linhas = [g.esperas.item(i, "values") for i in g.esperas.get_children()]
        self.assertEqual(linhas, [("P1", "1"), ("P2", "1")])

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
