from Qt.QtWidgets import QApplication
# work dir should be in directory fenx.studio

from tray_menu import tray_menu_class

if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    w = tray_menu_class.LauncherTrayMenu()
    app.exec_()
