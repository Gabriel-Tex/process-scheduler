"""Entrada do pacote portátil .pyz. A opção --verificar serve à validação do pacote."""
import json
import sys
import traceback
from pathlib import Path

from src.scheduler.gui.app_gui import AppGUI


def exigir(condicao, mensagem):
    """Não usar assert: python -O não deve desativar a verificação do pacote."""
    if not condicao:
        raise RuntimeError(mensagem)


def verificar_pacote(destino):
    """Testa a GUI e a execução real dentro do .pyz, sem depender do repositório."""
    app = None
    try:
        app = AppGUI()
        app.withdraw()
        app.entrada.carregar_texto("0 3 1\n1 1 1")
        app.config.lista.selection_clear(0, "end")
        app.config.lista.selection_set(app.config.algoritmos.index("rr"))
        app.executar()
        limite = app.after(10000, app.quit)

        def aguardar():
            if app._ocupado:
                app.after(10, aguardar)
            else:
                app.quit()

        app.after(10, aguardar)
        app.mainloop()
        app.after_cancel(limite)
        app.update()
        exigir(not app._ocupado, "A execução não terminou.")
        r = app.resultado.resultados[0]
        exigir([t.executando for t in r.registros] == ["P1", "P1", "P2", "P1"], "Sequência RR incorreta.")
        exigir(r.esperas == (("P1", 1), ("P2", 1)), "Tempos de espera incorretos.")
        exigir(len(app.gantt.esperas.get_children()) == 2, "Tabela de espera incompleta.")
        # Cobrir os imports dinâmicos dos dois algoritmos no pacote.
        resultados = app.controlador.executar("0 3 1\n1 1 2", "2", "1", ["rr_prio_aging"])
        exigir(resultados[0].nome_algoritmo == "Round-Robin + envelhecimento", "RR com envelhecimento indisponível.")
        app.gantt.finalizar()
        app.gantt.abas.select(1)
        app.update()
        app.gantt.abas.select(0)
        app.update()
        relatorio = {"ok": True, "empacotado": str(__file__).lower().replace("\\", "/").find(".pyz/") >= 0,
                     "esperas": r.esperas, "algoritmos": app.servico.listar_algoritmos()}
        codigo = 0
    except Exception:
        relatorio = {"ok": False, "erro": traceback.format_exc()}
        codigo = 1
    finally:
        if app is not None:
            app.fechar()
    Path(destino).write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return codigo


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--verificar":
        return verificar_pacote(sys.argv[2])
    AppGUI().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
