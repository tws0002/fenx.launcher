# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\work\fenx\launcher\tray_menu\widgets\login_dialog.ui'
#
# Created: Fri Feb 09 15:34:56 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_login(object):
    def setupUi(self, login):
        login.setObjectName("login")
        login.resize(348, 217)
        self.verticalLayout = QtGui.QVBoxLayout(login)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.logo_lb = QtGui.QLabel(login)
        self.logo_lb.setMinimumSize(QtCore.QSize(64, 64))
        self.logo_lb.setMaximumSize(QtCore.QSize(16777215, 100))
        self.logo_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_lb.setObjectName("logo_lb")
        self.horizontalLayout.addWidget(self.logo_lb)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(login)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.login_le = QtGui.QLineEdit(login)
        self.login_le.setObjectName("login_le")
        self.gridLayout.addWidget(self.login_le, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(login)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.password_le = QtGui.QLineEdit(login)
        self.password_le.setEchoMode(QtGui.QLineEdit.Password)
        self.password_le.setObjectName("password_le")
        self.gridLayout.addWidget(self.password_le, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.message_lb = QtGui.QLabel(login)
        self.message_lb.setText("")
        self.message_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.message_lb.setObjectName("message_lb")
        self.verticalLayout.addWidget(self.message_lb)
        self.submit_btn = QtGui.QPushButton(login)
        self.submit_btn.setObjectName("submit_btn")
        self.verticalLayout.addWidget(self.submit_btn)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.register_btn = QtGui.QPushButton(login)
        self.register_btn.setObjectName("register_btn")
        self.horizontalLayout_2.addWidget(self.register_btn)
        self.forgot_btn = QtGui.QPushButton(login)
        self.forgot_btn.setObjectName("forgot_btn")
        self.horizontalLayout_2.addWidget(self.forgot_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(login)
        QtCore.QMetaObject.connectSlotsByName(login)

    def retranslateUi(self, login):
        login.setWindowTitle(QtGui.QApplication.translate("login", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.logo_lb.setText(QtGui.QApplication.translate("login", "LOGO", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("login", "Email:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("login", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.submit_btn.setText(QtGui.QApplication.translate("login", "Submit", None, QtGui.QApplication.UnicodeUTF8))
        self.register_btn.setText(QtGui.QApplication.translate("login", "Register", None, QtGui.QApplication.UnicodeUTF8))
        self.forgot_btn.setText(QtGui.QApplication.translate("login", "Forgot Password", None, QtGui.QApplication.UnicodeUTF8))

