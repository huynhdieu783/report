from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.show
    def lienketnutlenh(self):
        self.pushButton.clicked.connect(self.lienketnutlenh)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())