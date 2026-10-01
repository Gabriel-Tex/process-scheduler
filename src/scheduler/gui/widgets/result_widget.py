"""Tabela comparativa; a seleção expõe o resultado ao painel de diagrama."""
from tkinter import ttk
from src.scheduler.gui.models import ResultadoGUI


class ResultadoWidget(ttk.LabelFrame):
    def __init__(self, master, ao_selecionar):
        super().__init__(master, text="03  Comparação", padding=10)
        self.resultados: list[ResultadoGUI] = []
        self.ao_selecionar = ao_selecionar
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tabela = ttk.Treeview(self, columns=("algoritmo", "tt", "tw", "trocas"),
                                  show="headings", height=2, selectmode="browse")
        for nome, titulo, largura in (
            ("algoritmo", "Algoritmo", 330), ("tt", "Tempo médio de vida (s)", 190),
            ("tw", "Tempo médio de espera (s)", 200), ("trocas", "Trocas de contexto", 160),
        ):
            self.tabela.heading(nome, text=titulo)
            self.tabela.column(nome, width=largura, minwidth=140,
                               anchor="w" if nome == "algoritmo" else "center")
        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.tabela.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)

    def atualizar(self, resultados):
        self.resultados = list(resultados)
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for i, r in enumerate(self.resultados):
            self.tabela.insert("", "end", iid=str(i), values=(
                r.nome_algoritmo, f"{r.tt_medio:.2f}".replace(".", ","),
                f"{r.tw_medio:.2f}".replace(".", ","), r.trocas_contexto))
        if self.resultados:
            self.tabela.selection_set("0")
            self.tabela.focus("0")
            self.ao_selecionar(self.resultados[0])

    def _selecionar(self, _evento=None):
        selecao = self.tabela.selection()
        if selecao:
            self.ao_selecionar(self.resultados[int(selecao[0])])
