"""Configuração e seleção de algoritmos registrados na fábrica."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.scheduler.io.config_reader import ler_configuracao
from src.scheduler.gui.services import NOMES_ALGORITMOS


class ConfigWidget(ttk.LabelFrame):
    def __init__(self, master, algoritmos, ao_alterar=lambda: None):
        super().__init__(master, text="02  Configuração", padding=12)
        self.ao_alterar = ao_alterar
        self.columnconfigure(0, weight=1)
        self.quantum = tk.StringVar(value="2")
        self.aging = tk.StringVar(value="1")
        numeros = ttk.Frame(self)
        numeros.grid(row=0, column=0, sticky="ew")
        for i, (nome, var) in enumerate((("Quantum (s)", self.quantum), ("Aging", self.aging))):
            ttk.Label(numeros, text=nome).grid(row=0, column=i, sticky="w")
            ttk.Entry(numeros, textvariable=var, width=10).grid(
                row=1, column=i, sticky="w", padx=(0, 14))
            var.trace_add("write", lambda *_: self.ao_alterar())
        ttk.Button(self, text="Carregar configuração", command=self.importar).grid(
            row=1, column=0, sticky="w", pady=(8, 10))
        ttk.Label(self, text="Algoritmos disponíveis", style="Strong.TLabel").grid(
            row=2, column=0, sticky="w")
        self.lista = tk.Listbox(self, selectmode="multiple", exportselection=False,
                               height=3, borderwidth=0, highlightthickness=1,
                               highlightbackground="#d7deea", background="white",
                               selectbackground="#dbeafe", selectforeground="#153e75",
                               font=("Segoe UI", 10), activestyle="dotbox")
        self.lista.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        self.rowconfigure(3, weight=1)
        self.algoritmos = list(algoritmos)
        for nome in self.algoritmos:
            self.lista.insert("end", NOMES_ALGORITMOS.get(nome, nome))
        if self.algoritmos:
            self.lista.selection_set(0, "end")
        self.lista.bind("<<ListboxSelect>>", lambda _: self.ao_alterar())

    def selecionados(self):
        return [self.algoritmos[i] for i in self.lista.curselection()]

    def importar(self):
        caminho = filedialog.askopenfilename(parent=self, title="Carregar configuração",
                                            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not caminho:
            return
        try:
            with open(caminho, encoding="utf-8-sig") as arquivo:
                config = ler_configuracao(arquivo)
            self.quantum.set(str(config.quantum))
            self.aging.set(str(config.aging))
        except (ValueError, OSError, UnicodeError) as erro:
            messagebox.showerror("Configuração inválida", str(erro), parent=self)
