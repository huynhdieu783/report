import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtChart import QBarSet, QBarSeries, QChart, QBarCategoryAxis, QValueAxis, QChartView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QInputDialog, \
    QMessageBox
from datetime import datetime

from login import User
from baocao import BaoCao
from chatbot import DifyAIService
from search import TimKiem
from menu import menu
from luulichsu import BuaAn, DanhsachBuaAn
from congthuc import TimKiemCongThuc


class NutriGenLogic:
    def __init__(self, main_app):
        self.main_app = main_app
        self.stack = main_app.stack
        self.user = None
        self.gender = "Nam"
        self.muc_do_van_dong = "trung_binh"
        self.ds_bua = DanhsachBuaAn()
        self.ds_bua.Doc("bua_an.json")
        self.chatbot = DifyAIService("app-9QjCula1qyNMMTvXU6grOrSQ")
        self.ql_cong_thuc = TimKiemCongThuc()
        self.loai_tim_kiem = "ten"

        self.chat_layout = None  # Sẽ khởi tạo tại setup_chat_ui

    def ket_noi_nut_bam(self):
        # Tạo từ điển tham chiếu nhanh đến các trang (p[1] là Index 0, ...)
        self.p = {i: self.stack.widget(i - 1) for i in range(1, 13)}

        # Khởi tạo khu vực Chatbot (Trang 11)
        self.setup_chat_ui()

        # --- ĐIỀU HƯỚNG CƠ BẢN ---
        self.p[1].btn_batdaungay.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.p[2].btn_tieptuc.clicked.connect(self.xu_ly_trang_2)
        self.p[3].btn_tinhtoan.clicked.connect(self.xu_ly_trang_3)

        # Menu chính (Trang 4)
        self.p[4].btn_timkiem.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.p[4].btn_congthuc.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.p[4].btn_luulichsu.clicked.connect(lambda: self.stack.setCurrentIndex(8))  # Trang 9
        self.p[4].btn_chatbot.clicked.connect(lambda: self.stack.setCurrentIndex(10))
        self.p[4].btn_baocao.clicked.connect(self.mo_trang_12)

        # Xử lý các nút Back
        for i in [5, 6, 9, 11, 12]:
            if hasattr(self.p[i], 'btnBack'):
                self.p[i].btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        self.p[10].btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(7))  # 10 -> 8
        self.p[8].btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(8))  # 8 -> 9
        self.p[7].btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(5))  # 7 -> 6

        # --- XỬ LÝ CHỨC NĂNG ---
        self.p[2].btn_nam.clicked.connect(lambda: self.chon_gioi_tinh("Nam"))
        self.p[2].btn_nu.clicked.connect(lambda: self.chon_gioi_tinh("Nữ"))
        self.p[5].txt_timkiemmonan.returnPressed.connect(self.tim_kiem_nhanh_trang_5)
        self.p[6].btn_timkiem.clicked.connect(self.tim_kiem_cong_thuc_trang_6)
        self.p[6].txt_hienketqua.itemDoubleClicked.connect(self.mo_trang_7_cong_thuc)

        # Nhật ký ăn uống
        self.p[8].btn_themsang.clicked.connect(lambda: self.mo_trang_9_nhap_lieu("sang"))
        self.p[8].btn_themtrua.clicked.connect(lambda: self.mo_trang_9_nhap_lieu("trua"))
        self.p[8].btn_themtoi.clicked.connect(lambda: self.mo_trang_9_nhap_lieu("toi"))
        self.p[8].btn_themsnack.clicked.connect(lambda: self.mo_trang_9_nhap_lieu("snack"))
        self.p[9].btn_them.clicked.connect(self.luu_bua_an)

        # Chatbot
        self.p[11].btnSend.clicked.connect(self.gui_tin_nhan_chatbot)

        # Trang 5 - Các nút gợi ý món ăn
        self.p[5].Goiy1.clicked.connect(lambda: self.hien_cong_thuc_goi_y("phobo"))
        self.p[5].Goiy2.clicked.connect(lambda: self.hien_cong_thuc_goi_y("buncha"))
        self.p[5].Goiy3.clicked.connect(lambda: self.hien_cong_thuc_goi_y("goicuon"))
        self.p[5].Goiy4.clicked.connect(lambda: self.hien_cong_thuc_goi_y("miquang"))

        # Nhật ký ăn uống - Chức năng chọn món để xóa
        self.p[8].btn_xoasang.clicked.connect(lambda: self.xoa_bua_an_co_lua_chon("Sáng"))
        self.p[8].btn_xoatrua.clicked.connect(lambda: self.xoa_bua_an_co_lua_chon("Trưa"))
        self.p[8].btn_xoatoi.clicked.connect(lambda: self.xoa_bua_an_co_lua_chon("Tối"))
        self.p[8].btn_xoasnack.clicked.connect(lambda: self.xoa_bua_an_co_lua_chon("Snack"))

    # --- HÀM TẠO KHUNG CHAT (MESSENGER STYLE) ---
    def setup_chat_ui(self):
        container = QtWidgets.QWidget()
        self.chat_layout = QVBoxLayout(container)
        self.chat_layout.setAlignment(QtCore.Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.p[11].scrollArea.setWidget(container)
        self.p[11].scrollArea.setWidgetResizable(True)

    def add_chat_bubble(self, text, is_user=True):
        h_layout = QHBoxLayout()
        bubble = QFrame()

        # Thiết kế khung tin nhắn
        if is_user:
            # Bạn: Bên phải, màu xanh nhạt
            bubble.setStyleSheet(
                "background-color: #DCF8C6; border-radius: 15px; border-bottom-right-radius: 2px; padding: 10px;")
            h_layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            h_layout.addWidget(bubble)
        else:
            # AI: Bên trái, màu xám trắng
            bubble.setStyleSheet(
                "background-color: #F0F0F0; border-radius: 15px; border-bottom-left-radius: 2px; padding: 10px; border: 1px solid #E0E0E0;")
            h_layout.addWidget(bubble)
            h_layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        v_inner = QVBoxLayout(bubble)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("background: transparent; border: none; color: black; font-size: 12px;")
        v_inner.addWidget(lbl)

        self.chat_layout.addLayout(h_layout)

        # Tự động cuộn xuống cuối
        QtCore.QTimer.singleShot(100, lambda: self.p[11].scrollArea.verticalScrollBar().setValue(
            self.p[11].scrollArea.verticalScrollBar().maximum()
        ))

    def gui_tin_nhan_chatbot(self):
        hoi = self.p[11].inputField.text().strip()
        if not hoi: return
        self.p[11].inputField.clear()

        # Thêm tin nhắn của bạn
        self.add_chat_bubble(hoi, is_user=True)

        # Gọi AI trả lời
        bc = BaoCao(self.user, self.muc_do_van_dong)
        tra_loi = self.chatbot.get_advice(self.user, bc, hoi)

        # Thêm tin nhắn AI
        self.add_chat_bubble(tra_loi, is_user=False)

    # --- LOGIC XỬ LÝ TRANG ---
    def chon_gioi_tinh(self, gt):
        self.gender = gt
        s_on = "background-color: #4ECDC4; color: white; border-radius: 10px;"
        s_off = "background-color: #f0f0f0; color: black; border-radius: 10px;"
        self.p[2].btn_nam.setStyleSheet(s_on if gt == "Nam" else s_off)
        self.p[2].btn_nu.setStyleSheet(s_on if gt == "Nữ" else s_off)

    def xu_ly_trang_2(self):
        try:
            ten = self.p[2].txt_hovaten.text()
            tuoi = int(self.p[2].txt_tuoi.text())
            can = float(self.p[2].txt_cannang.text())
            cao = float(self.p[2].txt_chieucao.text()) / 100
            self.user = User(ten, tuoi, self.gender, cao, can, can)
            self.stack.setCurrentIndex(2)
        except:
            pass

    def xu_ly_trang_3(self):
        try:
            self.user.aim = float(self.p[3].txt_cannangmongmuon.text())
            vd_map = {"Ít vận động": "it_van_dong", "Nhẹ nhàng": "nhe_nhang", "Trung bình": "trung_binh",
                      "Nặng": "nang", "Rất nặng": "rat_nang"}
            self.muc_do_van_dong = vd_map.get(self.p[3].comboBox.currentText(), "trung_binh")

            self.p[4].txt_hoten.setText(f"{self.user.name} | {self.user.age}")
            self.p[4].lbl_chieucao.setText(f"{self.user.height * 100} cm")
            self.p[4].lbl_cannang.setText(f"{self.user.weight} kg")
            self.p[4].lbl_BMI.setText(str(round(self.user.Tinh_BMI(), 1)))
            self.p[4].lbl_BMR.setText(f"{round(self.user.Tinh_BMR(), 0)} kcal")
            hieu = self.user.weight - self.user.aim
            self.p[4].lbl_muctieu.setText(f"bạn cần {'giảm' if hieu > 0 else 'tăng'} {round(abs(hieu), 1)} kg")
            self.stack.setCurrentIndex(3)
        except:
            pass

    def tim_kiem_nhanh_trang_5(self):
        ten = self.p[5].txt_timkiemmonan.text().strip()
        kq = TimKiem(ten).tim_kiem_mon_an()
        if kq:
            self.p[5].txt_lichsutimkiem.setPlainText(
                f"{kq['ten']} | Calo: {kq['calo']} | C: {kq['carb']} P: {kq['protein']} F: {kq['fat']}")

    def hien_cong_thuc_goi_y(self, key_mon):
        """Lấy thông tin món ăn từ menu và hiển thị lên Trang 7"""
        if key_mon in menu:
            data = menu[key_mon]

            # Đổ dữ liệu vào Trang 7 (Index 6)
            self.p[7].txt_tenmon.setText(data['ten'])

            # Hiển thị thông số dinh dưỡng
            dinh_duong = f"Calo: {data['calo']} | Carbs: {data['carb']}g | Protein: {data['protein']}g | Fat: {data['fat']}g"
            self.p[7].txt_thongtindinhduong.setText(dinh_duong)

            # Hiển thị các bước nấu
            self.p[7].txt_cacbuocnau.setPlainText(data.get('congthuc', "Đang cập nhật công thức..."))

            # Chuyển đến Trang 7 (Index 6)
            self.stack.setCurrentIndex(6)
        else:
            QMessageBox.warning(None, "Lỗi", "Dữ liệu món ăn gợi ý không tồn tại!")
    def tim_kiem_cong_thuc_trang_6(self):
        val = self.p[6].line1trang6.text()
        self.p[6].txt_hienketqua.clear()
        res = self.ql_cong_thuc.tim_theo_ten(val)
        for i, m in enumerate(res):
            self.p[6].txt_hienketqua.addItem(f"{i + 1}. {m.ten} - {m.calo} kcal")

    def mo_trang_7_cong_thuc(self, item):
        try:
            ten = item.text().split(". ")[1].split(" - ")[0]
            kq = TimKiem(ten).tim_kiem_mon_an()
            if kq:
                self.p[7].txt_tenmon.setText(kq['ten'])
                self.p[7].txt_thongtindinhduong.setText(f"C: {kq['carb']} | P: {kq['protein']} | F: {kq['fat']}")
                self.p[7].txt_cacbuocnau.setPlainText(kq.get('congthuc', ""))
                self.stack.setCurrentIndex(6)
        except:
            pass

    def mo_trang_9_nhap_lieu(self, bua):
        self.p[9].rad_sang.setChecked(bua == "sang")
        self.p[9].rad_trua.setChecked(bua == "trua")
        self.p[9].rad_toi.setChecked(bua == "toi")
        self.p[9].rad_snack.setChecked(bua == "snack")
        self.stack.setCurrentIndex(8)

    def cap_nhat_tong_dinh_duong_trang_8(self):
        """Cập nhật dữ liệu hiển thị cho Trang 8 dựa trên ngày hiện tại"""
        # 1. Lấy ngày hôm nay (YYYY-MM-DD)
        hom_nay = datetime.now().strftime("%Y-%m-%d")

        # 2. Khởi tạo tổng và danh sách tên món
        tong = {"calo": 0.0, "carb": 0.0, "pro": 0.0, "fat": 0.0}
        ten_cac_bua = {"Sáng": [], "Trưa": [], "Tối": [], "Snack": []}

        # 3. Duyệt file dữ liệu
        for b in self.ds_bua.danh_sach_bua:
            # Lọc theo ngày (chuỗi thời gian bắt đầu bằng YYYY-MM-DD)
            if b.thoi_gian.startswith(hom_nay):
                d = b.tinh_dinh_duong()
                tong["calo"] += d.get("calo", 0)
                tong["carb"] += d.get("carb", 0)
                tong["pro"] += d.get("protein", 0)
                tong["fat"] += d.get("fat", 0)

                # Lấy tên món từ menu (nếu không có thì dùng tên gốc)
                ten_dep = menu.get(b.ten_mon, {}).get("ten", b.ten_mon)
                if b.bua in ten_cac_bua:
                    ten_cac_bua[b.bua].append(ten_dep)

        # 4. Hiển thị lên các nhãn (Labels) của Trang 8
        # Các chỉ số tổng
        self.p[8].lbl_calo.setText(f"{round(tong['calo'], 0)}")
        self.p[8].lbl_carbs.setText(f"{round(tong['carb'], 1)}")
        self.p[8].lbl_protein.setText(f"{round(tong['pro'], 1)}")
        self.p[8].lbl_fat.setText(f"{round(tong['fat'], 1)}")

        # Danh sách món ăn (nối các món bằng dấu phẩy nếu một bữa ăn nhiều món)
        self.p[8].lbl_sang.setText(", ".join(ten_cac_bua["Sáng"]))
        self.p[8].lbl_trua.setText(", ".join(ten_cac_bua["Trưa"]))
        self.p[8].lbl_toi.setText(", ".join(ten_cac_bua["Tối"]))
        self.p[8].lbl_snack.setText(", ".join(ten_cac_bua["Snack"]))

    def luu_bua_an(self):
        """Hàm xử lý khi nhấn btn_them ở Trang 9"""
        try:
            ten_raw = self.p[9].txt_nhapmonan.text().strip()
            tk = TimKiem("")
            ten_key = tk.dichmon(ten_raw)  # Chuyển "Phở bò" -> "phobo"

            if ten_key not in menu:
                QMessageBox.warning(None, "Lỗi", f"Món '{ten_raw}' không có trong thực đơn!")
                return

            khau_phan = float(self.p[9].txt_nhapkhauphan.text())
            bua_chon = "Sáng" if self.p[9].rad_sang.isChecked() else \
                "Trưa" if self.p[9].rad_trua.isChecked() else \
                    "Tối" if self.p[9].rad_toi.isChecked() else "Snack"

            # Lưu vào danh sách và file JSON
            moi = BuaAn(ten_key, khau_phan, bua_chon)
            self.ds_bua.ThemBuaAN(moi)
            self.ds_bua.Luu()

            # --- CẬP NHẬT NGAY LẬP TỨC TRANG 8 ---
            self.cap_nhat_tong_dinh_duong_trang_8()

            # Logic chuyển trang dựa trên Calo mục tiêu
            bc = BaoCao(self.user, self.muc_do_van_dong)
            hom_nay = datetime.now().strftime("%Y-%m-%d")
            # Tính tổng calo nạp riêng ngày hôm nay để so sánh
            nap_hom_nay = sum(
                b.tinh_dinh_duong()["calo"] for b in self.ds_bua.danh_sach_bua if b.thoi_gian.startswith(hom_nay))
            limit = bc.tinh_calo_tieu_hao_ngay()

            if nap_hom_nay > limit:
                # Chuyển sang Trang 10 (Index 9) nếu vượt ngưỡng
                self.p[10].line1trang10.setText(f"bạn đã nạp dư {round(nap_hom_nay - limit, 0)} kcal")
                self.stack.setCurrentIndex(9)
            else:
                # Quay về Trang 8 (Index 7)
                self.stack.setCurrentIndex(7)

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", "Vui lòng nhập đúng định dạng số lượng!")

    def mo_trang_12(self):
        """Khởi chạy Trang 12 - Báo cáo & Biểu đồ"""
        if not self.user:
            QtWidgets.QMessageBox.warning(None, "Thông báo", "Vui lòng hoàn tất thông tin cá nhân trước!")
            return

        # 1. Đọc lại dữ liệu mới nhất từ file JSON để cập nhật biểu đồ
        self.ds_bua.Doc("bua_an.json")

        # 2. Tính toán tổng Calo nạp/tiêu để hiển thị lên nhãn txt_tongcalo
        bc = BaoCao(self.user, self.muc_do_van_dong)
        tong_nap = sum(b.tinh_dinh_duong()["calo"] for b in self.ds_bua.danh_sach_bua)
        tieu_hao = bc.tinh_calo_tieu_hao_ngay()

        # Hiển thị số liệu tổng quát lên Trang 12
        self.p[12].txt_tongcalo.setText(f"{round(tong_nap, 0)} / {round(tieu_hao, 0)} kcal")

        # 3. Kết nối các nút bấm chức năng (Dùng try-except disconnect để tránh lỗi bấm 1 lần chạy 2 lần)
        try:
            self.p[12].btnTheongay.clicked.disconnect()
        except:
            pass
        try:
            self.p[12].btnTheothang.clicked.disconnect()
        except:
            pass
        try:
            self.p[12].btnTheonam.clicked.disconnect()
        except:
            pass

        self.p[12].btnTheongay.clicked.connect(self.bieu_do_theo_ngay)
        self.p[12].btnTheothang.clicked.connect(self.bieu_do_theo_thang)
        self.p[12].btnTheonam.clicked.connect(self.bieu_do_theo_nam)

        # 4. Vẽ biểu đồ mặc định (hiện toàn bộ lịch sử) khi vừa mở trang
        self.ve_bieu_do_4_chi_so(self.ds_bua.danh_sach_bua, "Tổng quan dinh dưỡng")

        # 5. Chuyển đến Trang 12 (Index 11 trong StackedWidget)
        self.stack.setCurrentIndex(11)
        # Vẽ biểu đồ mặc định (tất cả dữ liệu)
        self.ve_bieu_do_4_chi_so(self.ds_bua.danh_sach_bua, "Tổng quan dinh dưỡng")
        self.stack.setCurrentIndex(11)

    def bieu_do_theo_ngay(self):
        val, ok = QInputDialog.getText(None, "Chọn ngày", "Nhập ngày (YYYY-MM-DD):",
                                       text=datetime.now().strftime("%Y-%m-%d"))
        if ok and val:
            ds_loc = [b for b in self.ds_bua.danh_sach_bua if b.thoi_gian.startswith(val)]
            self.ve_bieu_do_4_chi_so(ds_loc, f"Dinh dưỡng ngày {val}")

    def bieu_do_theo_thang(self):
        val, ok = QInputDialog.getText(None, "Chọn tháng", "Nhập tháng (YYYY-MM):",
                                       text=datetime.now().strftime("%Y-%m"))
        if ok and val:
            ds_loc = [b for b in self.ds_bua.danh_sach_bua if b.thoi_gian.startswith(val)]
            self.ve_bieu_do_4_chi_so(ds_loc, f"Dinh dưỡng tháng {val}")

    def bieu_do_theo_nam(self):
        val, ok = QInputDialog.getText(None, "Chọn năm", "Nhập năm (YYYY):", text=datetime.now().strftime("%Y"))
        if ok and val:
            ds_loc = [b for b in self.ds_bua.danh_sach_bua if b.thoi_gian.startswith(val)]
            self.ve_bieu_do_4_chi_so(ds_loc, f"Dinh dưỡng năm {val}")

    def ve_bieu_do_4_chi_so(self, filtered_list, title):
        """Vẽ biểu đồ dinh dưỡng 4 cột: Calo, Carb, Pro, Fat"""

        # 1. Kiểm tra dữ liệu: Nếu rỗng thì làm sạch vùng chứa và thoát
        target_widget = self.p[12].txt_khuyennghi
        if not filtered_list:
            self.xoa_layout_cu(target_widget)
            print("Dữ liệu rỗng, không vẽ biểu đồ.")
            return

        # 2. Xử lý dữ liệu: Gom tổng các chỉ số theo từng ngày
        data_day = {}
        for bua in filtered_list:
            # Lấy ngày (YYYY-MM-DD)
            ngay = bua.thoi_gian[:10] if hasattr(bua, 'thoi_gian') else "N/A"
            d = bua.tinh_dinh_duong()  # Lấy dict {calo, protein, carb, fat}

            if ngay not in data_day:
                data_day[ngay] = {"calo": 0, "carb": 0, "pro": 0, "fat": 0}

            data_day[ngay]["calo"] += d.get("calo", 0)
            data_day[ngay]["carb"] += d.get("carb", 0)
            data_day[ngay]["pro"] += d.get("protein", 0)
            data_day[ngay]["fat"] += d.get("fat", 0)

        sorted_days = sorted(data_day.keys())

        # 3. Khởi tạo 4 nhóm cột dữ liệu
        set_calo = QBarSet("Calo")
        set_carb = QBarSet("Carbs")
        set_pro = QBarSet("Protein")
        set_fat = QBarSet("Fat")

        # Đưa dữ liệu vào từng nhóm cột
        for day in sorted_days:
            set_calo.append(data_day[day]["calo"])
            set_carb.append(data_day[day]["carb"])
            set_pro.append(data_day[day]["pro"])
            set_fat.append(data_day[day]["fat"])

        # Thiết lập màu sắc (Mã màu hiện đại)
        set_calo.setColor(QColor("#4ECDC4"))  # Xanh ngọc
        set_carb.setColor(QColor("#FFD93D"))  # Vàng
        set_pro.setColor(QColor("#FF6B6B"))  # Đỏ nhạt
        set_fat.setColor(QColor("#6BCB77"))  # Xanh lá

        # 4. Tạo Series và Chart
        series = QBarSeries()
        series.append(set_calo)
        series.append(set_carb)
        series.append(set_pro)
        series.append(set_fat)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"📊 {title}")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)

        # 5. Cấu hình Trục X (Ngày tháng)
        axisX = QBarCategoryAxis()
        # Chỉ hiện 5 ký tự cuối (MM-DD) để tránh đè chữ
        axisX.append([d[-5:] for d in sorted_days])
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        # 6. Cấu hình Trục Y (Giá trị kcal/g)
        axisY = QValueAxis()
        # Tìm giá trị lớn nhất trong tất cả các cột để set giới hạn trục Y
        all_vals = []
        for v in data_day.values(): all_vals.extend(v.values())
        max_val = max(all_vals) if all_vals else 100
        axisY.setRange(0, max_val * 1.2)  # Cao hơn 20% so với giá trị max
        axisY.setLabelFormat("%.0f")
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # 7. Hiển thị lên QChartView
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)

        # 8. Cập nhật vào UI (Xử lý Layout)
        self.xoa_layout_cu(target_widget)

        if target_widget.layout() is None:
            layout = QVBoxLayout(target_widget)
            target_widget.setLayout(layout)
        else:
            layout = target_widget.layout()

        layout.addWidget(view)
        # Ép widget phản hồi kích thước ngay lập tức
        target_widget.setMinimumSize(600, 400)
        target_widget.update()

    def xoa_layout_cu(self, widget):
        """Hàm xóa sạch các widget cũ bên trong vùng chứa để vẽ mới"""
        if widget.layout() is not None:
            while widget.layout().count():
                item = widget.layout().takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
