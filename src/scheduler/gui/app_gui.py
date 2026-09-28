"""
Janela principal da interface gráfica — AppGUI (bônus).

Responsabilidades:
    - Criar e inicializar a janela principal (tkinter.Tk ou framework equivalente).
    - Instanciar e posicionar todos os widgets filhos:
        * EntradaWidget  — tabela editável de processos
        * ConfigWidget   — campos de quantum e aging
        * ResultadoWidget— exibição de tt/tw/trocas por algoritmo
        * GanttWidget    — diagrama de Gantt animado
    - Delegar toda lógica de negócio para ControladorGUI.

Padrão de projeto: MVC/MVP.
    - AppGUI é a View principal (apenas apresentação).
    - ControladorGUI é o Presenter/Controller (ponte com o simulador).
    - O simulador (motor.py) permanece completamente desacoplado da GUI.
"""
