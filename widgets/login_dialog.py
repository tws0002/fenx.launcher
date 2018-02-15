if False:
    from PySide.QtGui import *
    from PySide.QtCore import *
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
from fenx.tools import qt_ui_loader

login_dialog_UIs = qt_ui_loader.UiLoader.load('fenx.launcher.tray_menu.widgets.login_dialog_UIs')
if not login_dialog_UIs:
    raise Exception('Cant load UI module')
from fenx.config import settings
from fenx.resources import get_icon
import webbrowser, os


class LoginDialog(QDialog, login_dialog_UIs.Ui_login):
    submitSignal = Signal(str, str)

    def __init__(self,
                 parent=None,
                 submit_btn_text='Submit',
                 register_btn_text='Register',
                 forgot_btn_text='Forgot password',
                 add_register_btn=True,
                 add_forgot_btn=True,
                 register_url=None,
                 forgot_url=None,
                 title='Login',
                 logo=None):
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)
        self.submit_btn.setText(submit_btn_text)
        if not add_register_btn:
            self.register_btn.hide()
        else:
            self.register_btn.setText(register_btn_text)
            if register_url:
                self.register_btn.clicked.connect(lambda : webbrowser.open(register_url))
            else:
                self.register_btn.clicked.connect(lambda: self.show_message('Register URL not set'))
        if not add_forgot_btn:
            self.forgot_btn.hide()
        else:
            self.forgot_btn.setText(forgot_btn_text)
            if register_url:
                self.forgot_btn.clicked.connect(lambda : webbrowser.open(forgot_url))
            else:
                self.forgot_btn.clicked.connect(lambda: self.show_message('Restore URL not set'))
        self.setWindowFlags(Qt.Tool|Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title)
        self.submit_btn.clicked.connect(self.submit)
        self.set_logo(logo)

        self.login_le.setText(settings.USER_EMAIL or '')
        self.password_le.setText(settings.USER_PASSWORD or '')

    def submit(self):
        """
        Submit data
        """
        self.setDisabled(True)
        if not self.login_le.text():
            self.show_message('Login is required')
            self.setDisabled(False)
            return
        if not self.password_le.text():
            self.show_message('Password is required')
            self.setDisabled(False)
            return
        self.submitSignal.emit(self.login_le.text(), self.password_le.text())
        self.close()

    def show_message(self, msg, timeout=None):
        self.message_lb.setText(msg)
        if timeout:
            QTimer.singleShot(timeout*1000, lambda : self.message_lb.setText(''))

    def set_logo(self, path):
        path = get_icon(path)
        if path and os.path.exists(path):
            self.logo_lb.setPixmap(QPixmap(path).scaled(self.width(),self.logo_lb.height(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_lb.hide()
        self.resize(self.width(), 100)