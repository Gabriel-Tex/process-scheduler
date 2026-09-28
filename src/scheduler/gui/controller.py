"""
Controlador da GUI — ControladorGUI (bônus).

Responsabilidades (padrão MVC/MVP — Presenter/Controller):
    - Receber eventos dos widgets (ex.: botão "Executar") e traduzi-los em
      chamadas ao simulador.
    - Ler dados de EntradaWidget e ConfigWidget, construir Processo e Configuracao.
    - Invocar MotorSimulacao para cada algoritmo selecionado (mesmo motor da CLI).
    - Repassar ResultadoSimulacao para ResultadoWidget e GanttWidget exibirem.
    - Controlar a animação do Gantt (tick a tick com after() do tkinter ou similar).

Invariante:
    - Nunca duplica lógica de simulação — usa exatamente o mesmo MotorSimulacao da CLI.
    - Não faz print() — toda saída vai para os widgets.
"""
