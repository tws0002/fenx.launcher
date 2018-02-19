from Qt.QtWidgets import QApplication
# work dir should be in directory fenx.studio
import os, sys
sys.path.append(r'D:\work\fenx_pipeline\lib')
from fenx.launcher import main

if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    w = main.Launcher()
    app.exec_()
