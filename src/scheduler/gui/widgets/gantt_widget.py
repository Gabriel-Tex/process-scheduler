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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.titulo = ttk.Label(self, text="Selecione um resultado para visualizar.",
                                style="Strong.TLabel")
        self.titulo.grid(row=0, column=0, sticky="w", pady=(0, 6))
        barra = ttk.Frame(self)
        barra.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.botoes = []
        for texto, comando in (("Reproduzir", self.play), ("Pausar", self.pause),
                               ("Avançar", self.avancar_tick), ("Reiniciar", self.reiniciar)):
            b = ttk.Button(barra, text=texto, command=comando)
            b.pack(side="left", padx=(0, 5))
            self.botoes.append(b)
        ttk.Label(barra, text="Velocidade").pack(side="left", padx=(10, 5))
        self.velocidade = tk.StringVar(value="1x")
        ttk.Combobox(barra, textvariable=self.velocidade, values=("0,5x", "1x", "2x", "4x"),
                     state="readonly", width=5).pack(side="left")
        self.progresso = ttk.Label(barra, text="0 / 0 s", style="Muted.TLabel")
        self.progresso.pack(side="right")
        self.abas = ttk.Notebook(self)
        self.abas.grid(row=2, column=0, sticky="nsew")
        visual = ttk.Frame(self.abas)
        visual.rowconfigure(0, weight=1)
        visual.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(visual, background="white", highlightthickness=0, height=160)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h = ttk.Scrollbar(visual, orient="horizontal", command=self._rolar_x)
        v = ttk.Scrollbar(visual, orient="vertical", command=self._rolar_y)
        h.grid(row=1, column=0, sticky="ew")
        v.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=h.set, yscrollcommand=v.set)
        self.canvas.bind("<Configure>", lambda _: self._desenhar())
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
        ttk.Label(self, text="■ / ##  Executando     · / --  Esperando     Vazio  Ausente"
                  "     |     Cada coluna representa 1 segundo.",
                  style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self._habilitar(False)
        self.bind("<Destroy>", self._destruir)

    def _habilitar(self, habilitado):
        for botao in self.botoes:
            botao.state(["!disabled"] if habilitado else ["disabled"])

    def carregar(self, resultado):
        self.pause()
        self.resultado = resultado
        self.indice = 0
        self.titulo.configure(text=resultado.nome_algoritmo)
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", resultado.diagrama)
        self.texto.configure(state="disabled")
        self._habilitar(bool(resultado.registros))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self._desenhar()

    def _desenhar(self):
        c = self.canvas
        c.delete("all")
        r = self.resultado
        if r is None or r.registros is None or not r.registros:
            mensagem = "Execute uma simulação ou abra a demonstração."
            if r is not None:
                mensagem = "Registros de tempo indisponíveis. Consulte a aba Diagrama textual."
            c.create_text(20, 35, text=mensagem, anchor="w",
                          fill="#64748b", font=("Segoe UI", 10))
            c.configure(scrollregion=(0, 0, max(c.winfo_width(), 600), 100))
            self.progresso.configure(text="0 / 0 s")
            return
        total = len(r.registros)
        self.progresso.configure(text=f"{self.indice} / {total} s")
        x0, y0, largura, altura = 70, 30, 38, 30
        # Renderiza só a região visível; a rolagem continua cobrindo todo o diagrama.
        inicio = max(0, int((c.canvasx(0) - x0) // largura))
        fim = min(total, int((c.canvasx(c.winfo_width()) - x0) // largura) + 2)
        primeira_linha = max(0, int((c.canvasy(0) - y0) // altura))
        ultima_linha = min(len(r.ids_processos), int((c.canvasy(c.winfo_height()) - y0) // altura) + 2)
        for t in range(inicio, fim):
            c.create_text(x0 + t * largura + largura / 2, 15, text=str(t),
                          fill="#64748b", font=("Segoe UI", 9))
        for i in range(primeira_linha, ultima_linha):
            pid = r.ids_processos[i]
            y = y0 + i * altura
            c.create_text(35, y + altura / 2, text=pid, fill="#334155",
                          font=("Segoe UI", 10, "bold"))
            for t in range(inicio, fim):
                tick = r.registros[t]
                x = x0 + t * largura
                cor, marca, texto_cor = "#ffffff", "", "#64748b"
                if t < self.indice:
                    if tick.executando == pid:
                        cor, marca, texto_cor = CORES[i % len(CORES)], "##", "white"
                    elif pid in tick.presentes:
                        cor, marca = "#e2e8f0", "·"
                c.create_rectangle(x, y, x + largura, y + altura, fill=cor, outline="#edf0f5")
                if marca:
                    c.create_text(x + largura / 2, y + altura / 2,
                                  text=marca, fill=texto_cor, font=("Consolas", 10, "bold"))
        c.configure(scrollregion=(0, 0, x0 + total * largura + 20,
                                   y0 + len(r.ids_processos) * altura + 15))
        c.create_line(x0 + self.indice * largura, y0 - 4,
                      x0 + self.indice * largura, y0 + len(r.ids_processos) * altura,
                      fill="#1e293b", width=2)

    def _rolar_x(self, *args):
        self.canvas.xview(*args)
        self._desenhar()

    def _rolar_y(self, *args):
        self.canvas.yview(*args)
        self._desenhar()

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
            self._desenhar()

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
        self._desenhar()

    def _destruir(self, evento):
        if evento.widget is self:
            self.pause()
