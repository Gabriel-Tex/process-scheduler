"""Execute na raiz do projeto: python -m src.scheduler.gui."""
from .app_gui import AppGUI


def main():
    app = AppGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
