"""Janela principal. Widgets na thread Tk; simulação em worker sem acesso à UI."""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from .controller import ControladorGUI
from .services import ServicoReal, ServicoDemonstrativo
from .widgets.input_widget import EntradaWidget
from .widgets.config_widget import ConfigWidget
from .widgets.result_widget import ResultadoWidget
from .widgets.gantt_widget import GanttWidget


class AppGUI(tk.Tk):
    def __init__(self, servico=None):
        super().__init__()
        self.title("Simulador de Escalonamento • Sistemas Operacionais")
        self.geometry("1180x980")
        self.minsize(1000, 900)
        self.configure(background="#f3f6fb")
        self.servico = servico if servico is not None else ServicoReal()
        self.controlador = ControladorGUI(self.servico)
        self._ocupado = False
        self._demo = False
        self._versao_entrada = 0
        self._fila = queue.Queue()
        self._consulta = None
        self._estilo()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=3)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        cabecalho = ttk.Frame(self, padding=(20, 14))
        cabecalho.grid(row=0, column=0, sticky="ew")
        ttk.Label(cabecalho, text="Simulador de Escalonamento", style="Title.TLabel").pack(anchor="w")
        ttk.Label(cabecalho, text="Monte um cenário, compare políticas e acompanhe cada segundo.",
                  style="Muted.TLabel").pack(anchor="w", pady=(3, 0))
        superior = ttk.Frame(self, padding=(20, 0, 20, 10))
        superior.grid(row=1, column=0, sticky="nsew")
        superior.columnconfigure(0, weight=3)
        superior.columnconfigure(1, weight=2)
        superior.rowconfigure(0, weight=1)
        self.entrada = EntradaWidget(superior, self._entrada_alterada)
        self.entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.config = ConfigWidget(superior, self.servico.listar_algoritmos(), self._entrada_alterada)
        self.config.grid(row=0, column=1, sticky="nsew")
        self.gantt = GanttWidget(self)
        self.gantt.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.resultado = ResultadoWidget(self, self.gantt.carregar)
        self.resultado.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        rodape = ttk.Frame(self, padding=(20, 0, 20, 12))
        rodape.grid(row=4, column=0, sticky="ew")
        rodape.columnconfigure(0, weight=1)
        self.aviso = tk.StringVar(value="Nenhuma simulação executada.")
        self.rotulo_aviso = ttk.Label(rodape, textvariable=self.aviso, style="Status.TLabel",
                                     wraplength=690)
        self.rotulo_aviso.grid(row=0, column=0, sticky="w")
        acoes = ttk.Frame(rodape)
        acoes.grid(row=0, column=1, sticky="e")
        self.botao_demo = ttk.Button(acoes, text="Ver demonstração", command=self.demonstrar)
        self.botao_demo.pack(side="left", padx=(0, 8))
        self.botao_executar = ttk.Button(acoes, text="Executar simulação",
                                       style="Primary.TButton", command=self.executar)
        self.botao_executar.pack(side="left")
        self.motivo = self.servico.motivo_indisponivel() if hasattr(
            self.servico, "motivo_indisponivel") else None
        self.disponibilidade = ttk.Label(rodape, text=self.motivo or "Motor conectado • pronto para executar.",
                                        style="Muted.TLabel", wraplength=950)
        self.disponibilidade.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self._atualizar_botoes()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

    def _estilo(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10), background="#f3f6fb", foreground="#1e293b")
        estilo.configure("Title.TLabel", font=("Segoe UI", 21, "bold"))
        estilo.configure("Muted.TLabel", foreground="#64748b", font=("Segoe UI", 9))
        estilo.configure("Strong.TLabel", font=("Segoe UI", 10, "bold"))
        estilo.configure("Status.TLabel", foreground="#1d4ed8", font=("Segoe UI", 10, "bold"))
        estilo.configure("TLabelframe", bordercolor="#d7deea", relief="solid")
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground="#334155")
        estilo.configure("TButton", padding=(10, 5), background="#ffffff", bordercolor="#cbd5e1")
        estilo.map("TButton", background=[("active", "#e2e8f0")])
        estilo.configure("Primary.TButton", background="#2563eb", foreground="white")
        estilo.map("Primary.TButton", background=[("disabled", "#dbe3ef"), ("active", "#1d4ed8")],
                   foreground=[("disabled", "#64748b")])
        estilo.configure("Treeview", background="white", fieldbackground="white",
                         rowheight=25, bordercolor="#e2e8f0")
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e9eff7")
        estilo.map("Treeview", background=[("selected", "#dbeafe")],
                   foreground=[("selected", "#153e75")])
        estilo.configure("TNotebook.Tab", padding=(12, 5))

    def _entrada_alterada(self):
        self._versao_entrada += 1
        if hasattr(self, "aviso") and not self._demo and self.controlador.resultados:
            self.aviso.set("Entrada alterada • execute novamente para atualizar os resultados.")

    def _atualizar_botoes(self):
        self.botao_executar.state(["disabled"] if self._ocupado or self.motivo else ["!disabled"])
        self.botao_demo.state(["disabled"] if self._ocupado else ["!disabled"])

    def demonstrar(self):
        self._demo = True
        self.aviso.set("DEMONSTRAÇÃO • Dados fixos ilustrativos; não usa a entrada nem executa algoritmos.")
        self.resultado.atualizar(ServicoDemonstrativo.carregar())

    def executar(self):
        if self._ocupado or self.motivo:
            return
        # Capturar todos os valores Tk antes de criar a thread.
        valores = (self.entrada.obter_texto(), self.config.quantum.get(),
                   self.config.aging.get(), self.config.selecionados())
        try:
            self.controlador.validar_processos(valores[0])
            self.controlador.validar_config(valores[1], valores[2])
            if not valores[3]:
                raise ValueError("Selecione pelo menos um algoritmo.")
        except ValueError as erro:
            messagebox.showerror("Verifique os dados", str(erro), parent=self)
            return
        self.gantt.pause()
        self._ocupado = True
        self._versao_execucao = self._versao_entrada
        self._atualizar_botoes()
        self.aviso.set("Executando… Os resultados anteriores permanecem visíveis."
                       + (" DEMONSTRAÇÃO anterior." if self._demo else ""))

        def trabalhar():
            try:
                self._fila.put((self.controlador.executar(*valores), None))
            except Exception as erro:
                self._fila.put((None, erro))
        threading.Thread(target=trabalhar, daemon=True).start()
        self._consulta = self.after(50, self._receber)

    def _receber(self):
        self._consulta = None
        try:
            resultados, erro = self._fila.get_nowait()
        except queue.Empty:
            self._consulta = self.after(50, self._receber)
            return
        self._ocupado = False
        self._atualizar_botoes()
        if erro:
            self.aviso.set("Falha na execução; resultados anteriores preservados."
                           + (" DEMONSTRAÇÃO." if self._demo else ""))
            messagebox.showerror("Não foi possível simular", str(erro), parent=self)
            return
        self._demo = False
        self.resultado.atualizar(resultados)
        if self._versao_execucao != self._versao_entrada:
            self.aviso.set("Execução concluída • a entrada mudou durante a execução; execute novamente.")
        else:
            self.aviso.set("Simulação concluída • selecione um algoritmo para explorar o diagrama.")

    def fechar(self):
        self.gantt.pause()
        if self._consulta is not None:
            self.after_cancel(self._consulta)
            self._consulta = None
        self.destroy()
