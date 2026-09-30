"""Reprodução dos registros por tick, sem executar lógica de escalonamento."""
import tkinter as tk
from tkinter import ttk

CORES = ("#2563eb", "#0f766e", "#7c3aed", "#b45309", "#be185d", "#0369a1")


class GanttWidget(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="04  Linha do tempo", padding=10)
        self.resultado = None
        self.indice = 0
        self._agendamento = None
        self._tocando = False
        self._redesenho = None
        self._grade_chave = None
        self._pintado_ate = None
        self._celulas = {}
        self._cursor = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.titulo = ttk.Label(self, text="Selecione um resultado para visualizar.",
                                style="Strong.TLabel")
        self.titulo.grid(row=0, column=0, sticky="w", pady=(0, 6))
        barra = ttk.Frame(self)
        barra.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.botoes = []
        for texto, comando in (("Reproduzir", self.play), ("Pausar", self.pause),
                               ("Avançar", self.avancar_tick), ("Reiniciar", self.reiniciar),
                               ("Ir ao fim", self.finalizar)):
            b = ttk.Button(barra, text=texto, command=comando)
            b.pack(side="left", padx=(0, 5))
            self.botoes.append(b)
        ttk.Label(barra, text="Velocidade").pack(side="left", padx=(10, 5))
        self.velocidade = tk.StringVar(value="1x")
        ttk.Combobox(barra, textvariable=self.velocidade, values=("0,5x", "1x", "2x", "4x"),
                     state="readonly", width=5).pack(side="left")
        self.progresso = ttk.Label(barra, text="0 / 0 s", style="Muted.TLabel")
        self.progresso.pack(side="right")
        corpo = ttk.Frame(self)
        corpo.grid(row=2, column=0, sticky="nsew")
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)
        self.abas = ttk.Notebook(corpo)
        self.abas.grid(row=0, column=0, sticky="nsew")
        self.visual = visual = ttk.Frame(self.abas)
        visual.rowconfigure(0, weight=1)
        visual.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(visual, background="white", highlightthickness=0, height=160)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h = ttk.Scrollbar(visual, orient="horizontal", command=self._rolar_x)
        v = ttk.Scrollbar(visual, orient="vertical", command=self._rolar_y)
        h.grid(row=1, column=0, sticky="ew")
        v.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=h.set, yscrollcommand=v.set)
        self.canvas.bind("<Configure>", self._solicitar_desenho)
        self.abas.add(visual, text="  Gantt  ")
        textual = ttk.Frame(self.abas)
        textual.rowconfigure(0, weight=1)
        textual.columnconfigure(0, weight=1)
        self.texto = tk.Text(textual, wrap="none", font=("Consolas", 10),
                             background="white", relief="flat", height=6, state="disabled")
        self.texto.grid(row=0, column=0, sticky="nsew")
        texto_h = ttk.Scrollbar(textual, orient="horizontal", command=self.texto.xview)
        texto_v = ttk.Scrollbar(textual, orient="vertical", command=self.texto.yview)
        texto_h.grid(row=1, column=0, sticky="ew")
        texto_v.grid(row=0, column=1, sticky="ns")
        self.texto.configure(xscrollcommand=texto_h.set, yscrollcommand=texto_v.set)
        self.abas.add(textual, text="  Diagrama textual  ")
        self.abas.bind("<<NotebookTabChanged>>", self._solicitar_desenho)
        self.abas.enable_traversal()
        espera = ttk.Frame(corpo, padding=(10, 0, 0, 0))
        espera.grid(row=0, column=1, sticky="nsew")
        espera.columnconfigure(0, weight=1)
        espera.rowconfigure(1, weight=1)
        ttk.Label(espera, text="Espera por processo", style="Strong.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(4, 8))
        self.esperas = ttk.Treeview(espera, columns=("id", "espera"), show="headings",
                                   height=4, selectmode="none")
        self.esperas.heading("id", text="Processo")
        self.esperas.heading("espera", text="Total (s)")
        for coluna in ("id", "espera"):
            self.esperas.column(coluna, width=78, minwidth=65, anchor="center")
        self.esperas.grid(row=1, column=0, sticky="nsew")
        espera_v = ttk.Scrollbar(espera, orient="vertical", command=self.esperas.yview)
        espera_v.grid(row=1, column=1, sticky="ns")
        self.esperas.configure(yscrollcommand=espera_v.set)
        ttk.Label(espera, text="Execução completa", style="Muted.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(self, text="■ / ##  Executando     · / --  Esperando     Vazio  Ausente"
                  "     |     1 coluna = 1 s     |     Ctrl+Tab: alternar abas",
                  style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self._habilitar(False)
        self.bind("<Destroy>", self._destruir)

    def _habilitar(self, habilitado):
        for botao in self.botoes:
            botao.state(["!disabled"] if habilitado else ["disabled"])

    def carregar(self, resultado):
        # Treeview pode emitir duas notificações da mesma seleção.
        if resultado is self.resultado:
            return
        self.pause()
        self.resultado = resultado
        self.indice = 0
        self._grade_chave = None
        self._pintado_ate = None
        self.titulo.configure(text=resultado.nome_algoritmo)
        # O texto é preenchido uma única vez por resultado, nunca a cada aba/tick.
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", resultado.diagrama)
        self.texto.configure(state="disabled")
        for item in self.esperas.get_children():
            self.esperas.delete(item)
        totais = dict(resultado.esperas)
        for pid in resultado.ids_processos:
            self.esperas.insert("", "end", values=(pid, totais.get(pid, "—")))
        self._habilitar(bool(resultado.registros))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        total = len(resultado.registros or ())
        self.canvas.configure(scrollregion=(0, 0, 90 + total * 38,
                                           45 + len(resultado.ids_processos) * 30))
        self.progresso.configure(text=f"0 / {total} s")
        self._solicitar_desenho()

    def _solicitar_desenho(self, _evento=None):
        # Agrupa eventos de redimensionamento/abas em uma única atualização.
        if self._redesenho is None:
            self._redesenho = self.after_idle(self._atualizar_desenho)

    def _atualizar_desenho(self):
        self._redesenho = None
        self._desenhar()

    def _desenhar(self):
        # A animação pode continuar no texto; o Canvas escondido não consome CPU.
        if self.abas.select() != str(self.visual):
            return
        c, r = self.canvas, self.resultado
        if r is None or not r.registros:
            chave = ("vazio", id(r))
            if self._grade_chave != chave:
                c.delete("all")
                mensagem = "Execute uma simulação ou abra a demonstração."
                if r is not None:
                    mensagem = "Registros indisponíveis. Consulte o diagrama textual."
                c.create_text(20, 35, text=mensagem, anchor="w",
                              fill="#64748b", font=("Segoe UI", 10))
                c.configure(scrollregion=(0, 0, 600, 100))
                self._grade_chave = chave
            return
        total = len(r.registros)
        x0, y0, largura, altura = 70, 30, 38, 30
        inicio = max(0, int((c.canvasx(0) - x0) // largura))
        fim = min(total, int((c.canvasx(c.winfo_width()) - x0) // largura) + 2)
        primeira = max(0, int((c.canvasy(0) - y0) // altura))
        ultima = min(len(r.ids_processos), int((c.canvasy(c.winfo_height()) - y0) // altura) + 2)
        chave = (id(r), inicio, fim, primeira, ultima)

        if self._grade_chave != chave:
            # Cria só as células visíveis. Ticks apenas mudam suas cores/textos.
            c.delete("all")
            self._celulas.clear()
            for t in range(inicio, fim):
                c.create_text(x0 + t * largura + largura / 2, 15, text=str(t),
                              fill="#64748b", font=("Segoe UI", 9))
            for i in range(primeira, ultima):
                y = y0 + i * altura
                c.create_text(35, y + altura / 2, text=r.ids_processos[i],
                              fill="#334155", font=("Segoe UI", 10, "bold"))
                for t in range(inicio, fim):
                    x = x0 + t * largura
                    retangulo = c.create_rectangle(
                        x, y, x + largura, y + altura, fill="white", outline="#edf0f5")
                    texto = c.create_text(x + largura / 2, y + altura / 2, text="",
                                          font=("Consolas", 10, "bold"))
                    self._celulas[i, t] = (retangulo, texto)
            self._cursor = c.create_line(0, 0, 0, 0, fill="#1e293b", width=2)
            self._grade_chave = chave
            self._pintado_ate = None

        if self._pintado_ate == self.indice:
            return  # Pausado/finalizado: alternar abas reaproveita o desenho pronto.
        for (i, t), (retangulo, texto) in self._celulas.items():
            if self._pintado_ate is not None:
                if not min(self._pintado_ate, self.indice) <= t < max(self._pintado_ate, self.indice):
                    continue
            tick, pid = r.registros[t], r.ids_processos[i]
            cor, marca, texto_cor = "#ffffff", "", "#64748b"
            if t < self.indice:
                if tick.executando == pid:
                    cor, marca, texto_cor = CORES[i % len(CORES)], "##", "white"
                elif pid in tick.presentes:
                    cor, marca = "#e2e8f0", "·"
            c.itemconfigure(retangulo, fill=cor)
            c.itemconfigure(texto, text=marca, fill=texto_cor)
        c.coords(self._cursor, x0 + self.indice * largura, y0 - 4,
                 x0 + self.indice * largura, y0 + len(r.ids_processos) * altura)
        self._pintado_ate = self.indice

    def _rolar_x(self, *args):
        self.canvas.xview(*args)
        self._solicitar_desenho()

    def _rolar_y(self, *args):
        self.canvas.yview(*args)
        self._solicitar_desenho()

    def play(self):
        if not self.resultado or not self.resultado.registros or self._tocando:
            return
        if self.indice >= len(self.resultado.registros):
            self.indice = 0
        self._tocando = True
        self._passo_animado()

    def _passo_animado(self):
        self._agendamento = None
        if not self._tocando:
            return
        self._avancar()
        if self.indice < len(self.resultado.registros):
            fator = float(self.velocidade.get().replace("x", "").replace(",", "."))
            self._agendamento = self.after(round(500 / fator), self._passo_animado)
        else:
            self._tocando = False

    def _avancar(self):
        if self.resultado and self.resultado.registros:
            self.indice = min(self.indice + 1, len(self.resultado.registros))
            self.progresso.configure(text=f"{self.indice} / {len(self.resultado.registros)} s")
            self._solicitar_desenho()

    def avancar_tick(self):
        self.pause()
        self._avancar()

    def pause(self):
        self._tocando = False
        if self._agendamento is not None:
            self.after_cancel(self._agendamento)
            self._agendamento = None

    def reiniciar(self):
        self.pause()
        self.indice = 0
        self.canvas.xview_moveto(0)
        self.progresso.configure(text=f"0 / {len(self.resultado.registros or ()) if self.resultado else 0} s")
        self._solicitar_desenho()

    def finalizar(self):
        self.pause()
        if self.resultado and self.resultado.registros:
            self.indice = len(self.resultado.registros)
            self.progresso.configure(text=f"{self.indice} / {self.indice} s")
            self._solicitar_desenho()

    def _destruir(self, evento):
        if evento.widget is self:
            self.pause()
            if self._redesenho is not None:
                self.after_cancel(self._redesenho)
                self._redesenho = None
