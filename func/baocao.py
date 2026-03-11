import sys
import json
from datetime import datetime, timedelta
sys.path.append(r"D:\KTLT\baocao")
from login import User
from luulichsu import DanhsachBuaAn
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class BaoCao:
    HE_SO_HOAT_DONG = {
        "it_van_dong": 1.2,
        "nhe_nhang":   1.375,
        "trung_binh":  1.55,
        "nang":        1.725,
        "rat_nang":    1.9
    }

    def __init__(self, user: User, muc_do_van_dong="trung_binh",file_bua_an="bua_an.json"):
        self.user = user
        self.muc_do_van_dong = muc_do_van_dong
        self.lich_su = DanhsachBuaAn()  # ← dùng lại
        self.lich_su.Doc(file_bua_an)   # ← đọc dữ liệu

    # ─── Tính calo tiêu hao mỗi ngày (BMR × hệ số) ──────────────────────
    def tinh_calo_tieu_hao_ngay(self):
        bmr = self.user.Tinh_BMR()
        he_so = self.HE_SO_HOAT_DONG.get(self.muc_do_van_dong, 1.55)
        return round(bmr * he_so, 2)

    # ─── Tiến độ mục tiêu ────────────────────────────────────────────────
    def _tien_do(self, calo_nap_tb, calo_tieu_hao_ngay):
        calo_min, calo_max = self.user.Calo_ngay()
        calo_net_tb = round(calo_nap_tb - calo_tieu_hao_ngay, 2)

        if calo_nap_tb > calo_max:
            trang_thai = f"Vượt mục tiêu ({calo_nap_tb:.0f} > {calo_max} kcal/ngày)"
        elif calo_nap_tb < calo_min:
            trang_thai = f"Thấp hơn mục tiêu ({calo_nap_tb:.0f} < {calo_min} kcal/ngày)"
        else:
            trang_thai = f"Đạt mục tiêu ({calo_min} - {calo_max} kcal/ngày)"

        return {
            "trang_thai": trang_thai,
            "calo_nap_trung_binh_ngay": calo_nap_tb,
            "calo_tieu_hao_trung_binh_ngay": calo_tieu_hao_ngay,
            "calo_net_trung_binh_ngay": calo_net_tb
        }

    # ─── Khuyến nghị ─────────────────────────────────────────────────────
    def _khuyen_nghi(self, tong, so_ngay):
        kn = []
        calo_min, calo_max = self.user.Calo_ngay()
        calo_tb    = tong["calo"]    / so_ngay if so_ngay else 0
        protein_tb = tong["protein"] / so_ngay if so_ngay else 0
        fat_tb     = tong["fat"]     / so_ngay if so_ngay else 0

        if calo_tb > calo_max:
            kn.append("Giảm khẩu phần hoặc chọn món ít calo hơn")
        elif calo_tb < calo_min:
            kn.append("Tăng khẩu phần hoặc bổ sung thêm bữa phụ")
        if protein_tb < 50:
            kn.append("Bổ sung thêm protein (thịt, cá, trứng, đậu)")
        if fat_tb > 65:
            kn.append("Hạn chế chất béo, ưu tiên món luộc/hấp thay vì chiên")
        if not kn:
            kn.append("Chế độ ăn đang cân bằng, hãy duy trì!")
        return kn

    # ─── Tạo dict báo cáo từ kết quả thống kê ───────────────────────────
    def _tao_bao_cao(self, loai, thong_ke, so_ngay):
        tong = thong_ke["tong_dinh_duong"]
        calo_tieu_hao_ngay = self.tinh_calo_tieu_hao_ngay()
        calo_nap_tb = round(tong["calo"] / so_ngay, 2) if so_ngay else 0

        return {
            "loai": loai,
            "nguoi_dung": {
                "ten": self.user.name,
                "can_nang": self.user.weight,
                "muc_tieu": self.user.aim,
                "muc_do_van_dong": self.muc_do_van_dong,
                "bmr": round(self.user.Tinh_BMR(), 2),
                "calo_tieu_hao_moi_ngay": calo_tieu_hao_ngay
            },
            "so_ngay": so_ngay,
            "so_bua": len(thong_ke["danh_sach_bua_an"]),
            "tong_dinh_duong": tong,
            "phan_tich": self._tien_do(calo_nap_tb, calo_tieu_hao_ngay),
            "khuyen_nghi": self._khuyen_nghi(tong, so_ngay),
            "thoi_gian_tao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # ─── Lưu báo cáo ra JSON ─────────────────────────────────────────────
    def _luu_bao_cao(self, bao_cao, ten_file):
        with open(ten_file, "w", encoding="utf-8") as f:
            json.dump(bao_cao, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu báo cáo: {ten_file}")
        return bao_cao

    # ─── Báo cáo theo tuần ───────────────────────────────────────────────
    def bao_cao_tuan(self, ngay_bat_dau=None):
        thong_ke = self.lich_su.ThongKeTheoTuan(ngay_bat_dau)  # ← dùng lại
        tu_ngay, den_ngay = thong_ke["tuan"].split(" → ")
        so_ngay = (datetime.strptime(den_ngay, "%Y-%m-%d") -
                   datetime.strptime(tu_ngay, "%Y-%m-%d")).days + 1
        bc = self._tao_bao_cao(f"TUẦN ({thong_ke['tuan']})", thong_ke, so_ngay)
        return self._luu_bao_cao(bc, f"bao_cao_tuan_{tu_ngay}.json")

    # ─── Báo cáo theo tháng ──────────────────────────────────────────────
    def bao_cao_thang(self, thang=None, nam=None):
        thong_ke = self.lich_su.ThongKeTheoThang(thang, nam)   # ← dùng lại
        thang_str = thong_ke["thang"]
        # Tính số ngày trong tháng
        thang = int(thang_str.split("-")[1])
        nam   = int(thang_str.split("-")[0])
        tu_ngay  = f"{thang_str}-01"
        den_ngay = (datetime(nam, thang % 12 + 1, 1) -
                    timedelta(days=1)).strftime("%Y-%m-%d") \
                    if thang != 12 else f"{nam}-12-31"
        so_ngay = (datetime.strptime(den_ngay, "%Y-%m-%d") -
                   datetime.strptime(tu_ngay, "%Y-%m-%d")).days + 1
        bc = self._tao_bao_cao(f"THÁNG ({thang_str})", thong_ke, so_ngay)
        return self._luu_bao_cao(bc, f"bao_cao_thang_{thang_str}.json")

    def ve_bar_chart(self, bao_cao: dict) -> QChartView:
        # Gom calo theo ngày
        calo_theo_ngay = {}
        for bua in self.lich_su.danh_sach:
            ngay = bua.ngay if hasattr(bua, "ngay") else str(bua)[:10]
            calo_theo_ngay.setdefault(ngay, 0)
            calo_theo_ngay[ngay] += bua.calo if hasattr(bua, "calo") else 0

        ngay_list = sorted(calo_theo_ngay.keys())
        calo_list = [calo_theo_ngay[n] for n in ngay_list]
        nhan_x = [n[-5:] for n in ngay_list]  # dd/MM

        bar = QBarSet("Calo nạp")
        bar.setColor(QColor("#4ECDC4"))
        bar.append(calo_list)

        series = QBarSeries()
        series.append(bar)

        truc_x = QBarCategoryAxis()
        truc_x.append(nhan_x)

        truc_y = QValueAxis()
        truc_y.setTitleText("kcal")
        truc_y.setRange(0, max(calo_list) * 1.2 if calo_list else 100)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Calo nạp mỗi ngày — {bao_cao['loai']}")
        chart.addAxis(truc_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(truc_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(truc_x)
        series.attachAxis(truc_y)
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return view