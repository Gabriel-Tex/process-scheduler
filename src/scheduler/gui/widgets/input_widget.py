"""Editor de processos. A validação é compartilhada com a entrada textual."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from src.scheduler.gui.controller import ControladorGUI

EXEMPLO = "0 5 2\n0 2 3\n1 4 1\n3 3 4"


class EntradaWidget(ttk.LabelFrame):
    def __init__(self, master, ao_alterar=lambda: None):
        super().__init__(master, text="01  Processos", padding=12)
        self.ao_alterar = ao_alterar
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="Cadastre processos ou importe um arquivo de entrada.",
                  style="Muted.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        grade = ttk.Frame(self)
        grade.grid(row=1, column=0, sticky="nsew")
        grade.columnconfigure(0, weight=1)
        grade.rowconfigure(0, weight=1)
        self.tabela = ttk.Treeview(grade, columns=("id", "chegada", "duracao", "prioridade"),
                                  show="headings", height=3, selectmode="browse")
        for coluna, titulo in zip(self.tabela["columns"],
                                  ("ID", "Chegada (s)", "Duração (s)", "Prioridade")):
            self.tabela.heading(coluna, text=titulo)
            self.tabela.column(coluna, width=90, minwidth=65, anchor="center")
        self.tabela.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(grade, orient="vertical", command=self.tabela.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=scroll.set)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)
        self.campos = [tk.StringVar(value=v) for v in ("0", "1", "1")]
        formulario = ttk.Frame(self)
        formulario.grid(row=2, column=0, sticky="ew", pady=(10, 6))
        for i, (titulo, var) in enumerate(zip(("Chegada", "Duração", "Prioridade"), self.campos)):
            formulario.columnconfigure(i, weight=1)
            ttk.Label(formulario, text=titulo).grid(row=0, column=i, sticky="w")
            ttk.Entry(formulario, textvariable=var, width=9).grid(
                row=1, column=i, sticky="ew", padx=(0, 8))
        ttk.Button(formulario, text="Adicionar", command=self.adicionar).grid(row=1, column=3)
        ttk.Button(formulario, text="Editar", command=self.editar).grid(
            row=1, column=4, padx=(6, 0))
        acoes = ttk.Frame(self)
        acoes.grid(row=3, column=0, sticky="ew")
        for texto, comando in (("Remover", self.remover), ("Limpar", self.limpar),
                               ("Carregar arquivo", self.importar),
                               ("Carregar exemplo", lambda: self.carregar_texto(EXEMPLO))):
            ttk.Button(acoes, text=texto, command=comando).pack(side="left", padx=(0, 6))

    def obter_texto(self):
        return "\n".join(" ".join(map(str, self.tabela.item(i, "values")[1:]))
                         for i in self.tabela.get_children())

    def _valores_formulario(self):
        valores = [var.get().strip() for var in self.campos]
        for nome, valor in zip(("Chegada", "Duração", "Prioridade"), valores):
            try:
                int(valor)
            except ValueError:
                raise ValueError(f"{nome}: informe um número inteiro.")
        p = ControladorGUI.validar_processos(" ".join(valores))[0]
        return (p.instante_criacao, p.tempo_processamento, p.prioridade_estatica)

    def adicionar(self):
        try:
            valores = self._valores_formulario()
            self.tabela.insert("", "end", values=("", *valores))
            self._alterado()
        except ValueError as erro:
            messagebox.showerror("Verifique o processo", str(erro), parent=self)

    def editar(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Editar processo", "Selecione uma linha para editar.", parent=self)
            return
        try:
            valores = self._valores_formulario()
            self.tabela.item(selecionados[0], values=("", *valores))
            self._alterado()
        except ValueError as erro:
            messagebox.showerror("Verifique o processo", str(erro), parent=self)

    def _selecionar(self, _evento=None):
        if self.tabela.selection():
            valores = self.tabela.item(self.tabela.selection()[0], "values")[1:]
            for var, valor in zip(self.campos, valores):
                var.set(valor)

    def _alterado(self):
        # IDs seguem a ordem atual das linhas, inclusive após remoções.
        for n, item in enumerate(self.tabela.get_children(), 1):
            valores = self.tabela.item(item, "values")
            self.tabela.item(item, values=(f"P{n}", *valores[1:]))
        self.ao_alterar()

    def remover(self):
        for item in self.tabela.selection():
            self.tabela.delete(item)
        self._alterado()

    def limpar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._alterado()

    def carregar_texto(self, texto):
        # Validar tudo antes de substituir a tabela, preservando-a em caso de erro.
        try:
            processos = ControladorGUI.validar_processos(texto)
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro), parent=self)
            return False
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for p in processos:
            self.tabela.insert("", "end", values=(
                p.id, p.instante_criacao, p.tempo_processamento, p.prioridade_estatica))
        self.ao_alterar()
        return True

    def importar(self):
        caminho = filedialog.askopenfilename(parent=self, title="Carregar processos",
                                            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if caminho:
            try:
                self.carregar_texto(Path(caminho).read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError) as erro:
                messagebox.showerror("Não foi possível abrir o arquivo", str(erro), parent=self)
