import sys
import os
import importlib.util
from PyQt5 import QtWidgets, uic, QtCore
from main import NutriGenLogic



class NutriGenApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NUTRI-GEN AI")
        self.showMaximized()

        # 1. Thiết lập ảnh nền cho cửa sổ chính
        self.setStyleSheet("""
            QMainWindow {
                background-image: url(assets/Background.png);
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            }
        """)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        # 2. Stack Widget để chứa 12 trang
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setFixedSize(1100, 750)
        self.stack.setStyleSheet("background: transparent;")  # Stack luôn trong suốt
        self.layout.addWidget(self.stack, 0, 0, QtCore.Qt.AlignCenter)

        # 3. Nạp 12 file .ui
        self.load_ui_pages()

        # 4. Kết nối Logic điều hướng
        self.logic = NutriGenLogic(self)
        self.logic.ket_noi_nut_bam()

    def load_ui_pages(self):
        folder = "assets"
        for i in range(1, 13):
            ui_path = os.path.join(folder, f"trang{i}.ui")
            # Nạp Resource để hiện icon/khung ô (nếu có file _rc.py)
            rc_name = f"assets.trang{i}_rc"

            if os.path.exists(ui_path):
                try:
                    if importlib.util.find_spec(rc_name):
                        importlib.import_module(rc_name)

                    page = uic.loadUi(ui_path)

                    # CÁCH FIX MẤT NỀN Ô NHẬP LIỆU:
                    # Chỉ làm lớp nền của "trang" trong suốt, không ảnh hưởng đến các ô con
                    page.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

                    self.stack.addWidget(page)
                except Exception as e:
                    print(f"Lỗi nạp trang {i}: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NutriGenApp()
    window.show()
    sys.exit(app.exec_())