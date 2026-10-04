import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app_window import AppWindow

def main():
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
