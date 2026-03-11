import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi

HE_SO_HOAT_DONG = {
    "Ít vận động": 1.2,
    "Nhẹ nhàng":   1.375,
    "Trung bình":  1.55,
    "Nặng":        1.725,
    "Rất nặng":    1.9
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)

        # Kết nối sự kiện khi người dùng thay đổi lựa chọn
        self.comboBox.currentTextChanged.connect(self.khi_chon_muc_do)

        # Hiển thị giá trị mặc định khi mở
        self.khi_chon_muc_do(self.comboBox.currentText())

    def khi_chon_muc_do(self, gia_tri):
        muc_do = gia_tri.strip()
        he_so  = HE_SO_HOAT_DONG.get(muc_do, 1.55)
        self.statusbar.showMessage(f"Mức độ: {muc_do}  |  Hệ số: {he_so}")
        print(f"Chọn: {muc_do} → Hệ số: {he_so}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())