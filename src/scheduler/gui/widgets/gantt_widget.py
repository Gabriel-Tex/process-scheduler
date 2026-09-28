"""
Widget de Gantt animado — GanttWidget (bônus).

Responsabilidades:
    - Renderizar um diagrama de Gantt visual (canvas ou grid de células coloridas).
    - Animar tick a tick: revelar uma coluna de tempo por vez com delay configurável.
    - Cada processo é uma linha; cada tick é uma coluna.
    - Código de cores:
        * Cor sólida (processo executando)
        * Cinza claro (processo pronto/aguardando)
        * Branco / sem preenchimento (não chegou ou já terminou)
    - Controles: Play, Pause, Step, velocidade (delay entre ticks).
    - Recebe os dados brutos de DiagramaTempo (não o texto formatado) para
      poder colorir por estado — o controlador deve repassar a estrutura interna.

Interface pública:
    GanttWidget.carregar(diagrama: DiagramaTempo) -> None
    GanttWidget.play() -> None
    GanttWidget.pause() -> None
    GanttWidget.avancar_tick() -> None
"""
