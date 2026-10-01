"""Configuração e seleção de algoritmos registrados na fábrica."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.scheduler.io.config_reader import ler_configuracao
from src.scheduler.gui.services import NOMES_ALGORITMOS, ALGORITMOS_PREEMPTIVOS


class ConfigWidget(ttk.LabelFrame):
    def __init__(self, master, algoritmos, ao_alterar=lambda: None):
        super().__init__(master, text="02  Configuração", padding=12)
        self.ao_alterar = ao_alterar
        self.columnconfigure(0, weight=1)
        self.quantum = tk.StringVar(value="2")
        self.aging = tk.StringVar(value="1")
        self.permitir_preempcao = tk.BooleanVar(value=True)
        self._todos_algoritmos = list(algoritmos)
        self._entradas_numericas = []
        numeros = ttk.Frame(self)
        numeros.grid(row=0, column=0, sticky="ew")
        for i, (nome, var) in enumerate((("Quantum (s)", self.quantum), ("Aging", self.aging))):
            ttk.Label(numeros, text=nome).grid(row=0, column=i, sticky="w")
            entrada = ttk.Entry(numeros, textvariable=var, width=10)
            entrada.grid(row=1, column=i, sticky="w", padx=(0, 14))
            self._entradas_numericas.append(entrada)
            var.trace_add("write", lambda *_: self.ao_alterar())
        ttk.Button(self, text="Carregar configuração", command=self.importar).grid(
            row=1, column=0, sticky="w", pady=(8, 10))
        ttk.Checkbutton(self, text="Permitir preempção", variable=self.permitir_preempcao,
                        command=self._atualizar_lista).grid(row=2, column=0, sticky="w")
        self.dica = ttk.Label(self, style="Muted.TLabel", wraplength=280)
        self.dica.grid(row=3, column=0, sticky="w", pady=(3, 6))
        ttk.Label(self, text="Algoritmos disponíveis", style="Strong.TLabel").grid(
            row=4, column=0, sticky="w")
        self.lista = tk.Listbox(self, selectmode="multiple", exportselection=False,
                               height=3, borderwidth=0, highlightthickness=1,
                               highlightbackground="#d7deea", background="white",
                               selectbackground="#dbeafe", selectforeground="#153e75",
                               font=("Segoe UI", 10), activestyle="dotbox")
        self.lista.grid(row=5, column=0, sticky="nsew", pady=(5, 0))
        self.rowconfigure(5, weight=1)
        self._atualizar_lista()
        self.lista.bind("<<ListboxSelect>>", self._selecao_alterada)

    def _atualizar_lista(self):
        permitir = self.permitir_preempcao.get()
        self.algoritmos = [nome for nome in self._todos_algoritmos
                           if permitir or nome not in ALGORITMOS_PREEMPTIVOS]
        self.lista.delete(0, "end")
        for nome in self.algoritmos:
            self.lista.insert("end", NOMES_ALGORITMOS.get(nome, nome))
        if self.algoritmos:
            self.lista.selection_set(0, "end")
        self.dica.configure(text=("RR exige quantum > 0; zero não desativa o quantum."
                                 if permitir else "Sem preempção: FCFS, SJF e Prioridade cooperativa."))
        self._selecao_alterada()

    def _selecao_alterada(self, _evento=None):
        escolhidos = set(self.selecionados())
        self._entradas_numericas[0].state(
            ["!disabled"] if escolhidos.intersection({"rr", "rr_prio_aging"}) else ["disabled"])
        self._entradas_numericas[1].state(
            ["!disabled"] if "rr_prio_aging" in escolhidos else ["disabled"])
        self.ao_alterar()

    def valores_config(self):
        """Campos não aplicáveis não bloqueiam algoritmos sem quantum/aging."""
        escolhidos = set(self.selecionados())
        quantum = self.quantum.get() if escolhidos.intersection({"rr", "rr_prio_aging"}) else "2"
        aging = self.aging.get() if "rr_prio_aging" in escolhidos else "1"
        return quantum, aging

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
