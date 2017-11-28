import sys
from PyQt5 import QtWidgets
import mes_form
from client import *

class MyWindow(QtWidgets.QWidget, User):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        super().__init__(self)
        self.ui = mes_form.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.)



if __name__ == '__main__':


    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

