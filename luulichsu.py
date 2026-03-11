import sys
import json
sys.path.append(r"D:\KTLT\baocao")
from menu import menu
from login import User
from datetime import datetime, timedelta


class BuaAn:
    def __init__(self, ten_mon, khau_phan, bua, thoi_gian=None):
        self.ten_mon = ten_mon
        self.khau_phan = khau_phan
        self.bua = bua
        self.thoi_gian = thoi_gian if thoi_gian else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def date(self):
        return self.thoi_gian.split(" ")[0]

    def tinh_dinh_duong(self):
        he_so = self.khau_phan / 100
        mon = menu[self.ten_mon]
        return {
            "calo": round(mon["calo"] * he_so, 2),
            "protein": round(mon["protein"] * he_so, 2),
            "carb": round(mon["carb"] * he_so, 2),
            "fat": round(mon["fat"] * he_so, 2)
        }


class DanhsachBuaAn:
    def __init__(self):
        self.danh_sach_bua = []

    def ThemBuaAN(self, bua_an):
        for b in self.danh_sach_bua:
            if b.ten_mon == bua_an.ten_mon and b.bua == bua_an.bua:
                return True
        self.danh_sach_bua.append(bua_an)
        return False

    def XoaBuaAn(self, ten_mon):
        for b in self.danh_sach_bua:
            if b.ten_mon == ten_mon:
                self.danh_sach_bua.remove(b)
                return True
        return False

    def TimKiemBuaAn(self, tu_khoa):
        ket_qua = []
        for b in self.danh_sach_bua:
            if tu_khoa.lower() in b.ten_mon.lower() or tu_khoa == b.ten_mon:
                ket_qua.append(b)
        return ket_qua

    def TinhTongDinhDuong(self):
        tong = {"calo": 0, "protein": 0, "carb": 0, "fat": 0}
        for b in self.danh_sach_bua:
            dd = b.tinh_dinh_duong()
            for key in tong:
                tong[key] += dd[key]
        return tong
    
    def CanhBao(self, user: User):
        tong = self.TinhTongDinhDuong()
        calo_min, calo_max = user.Calo_ngay()

        if tong["calo"] > calo_max:
            return f"Cảnh báo: Lượng calo ({tong['calo']}) vượt quá mục tiêu ({calo_min} - {calo_max})!"
        elif tong["calo"] < calo_min:
            return f"Cảnh báo: Lượng calo ({tong['calo']}) thấp hơn mục tiêu ({calo_min} - {calo_max})!"
        else:
            return f"Lượng calo ({tong['calo']}) nằm trong mục tiêu ({calo_min} - {calo_max})!"

    def ThongKeTheoNgay(self, ngay=None):
        ngay = ngay if ngay else datetime.now().strftime("%Y-%m-%d")
        ket_qua = [b for b in self.danh_sach_bua if b.date == ngay]

        tong = {"calo": 0, "protein": 0, "carb": 0, "fat": 0}
        for b in ket_qua:
            dd = b.tinh_dinh_duong()
            for key in tong:
                tong[key] += dd[key]

        return {
            "ngay": ngay,
            "danh_sach_bua_an": [{"ten_mon": b.ten_mon, "khau_phan": b.khau_phan,
                                   "bua": b.bua, "thoi_gian": b.thoi_gian} for b in ket_qua],
            "tong_dinh_duong": tong
        }

    def ThongKeTheoTuan(self, ngay_bat_dau=None):
        # Nếu không truyền thì lấy thứ 2 của tuần hiện tại
        if ngay_bat_dau is None:
            hom_nay = datetime.now()
            ngay_bat_dau = hom_nay - timedelta(days=hom_nay.weekday())
        else:
            ngay_bat_dau = datetime.strptime(ngay_bat_dau, "%Y-%m-%d")

        ngay_ket_thuc = ngay_bat_dau + timedelta(days=6)
        tu_ngay  = ngay_bat_dau.strftime("%Y-%m-%d")
        den_ngay = ngay_ket_thuc.strftime("%Y-%m-%d")

        ket_qua = [b for b in self.danh_sach_bua if tu_ngay <= b.date <= den_ngay]

        tong = {"calo": 0, "protein": 0, "carb": 0, "fat": 0}
        for b in ket_qua:
            dd = b.tinh_dinh_duong()
            for key in tong:
                tong[key] += dd[key]

        return {
            "tuan": f"{tu_ngay} → {den_ngay}",
            "danh_sach_bua_an": [{"ten_mon": b.ten_mon, "khau_phan": b.khau_phan,
                                   "bua": b.bua, "thoi_gian": b.thoi_gian} for b in ket_qua],
            "tong_dinh_duong": tong
        }

    def ThongKeTheoThang(self, thang=None, nam=None):
        thang = thang if thang else datetime.now().month
        nam = nam if nam else datetime.now().year
        thang_str = f"{nam}-{thang:02d}"

        ket_qua = [b for b in self.danh_sach_bua if b.date.startswith(thang_str)]

        tong = {"calo": 0, "protein": 0, "carb": 0, "fat": 0}
        for b in ket_qua:
            dd = b.tinh_dinh_duong()
            for key in tong:
                tong[key] += dd[key]

        return {
            "thang": thang_str,
            "danh_sach_bua_an": [{"ten_mon": b.ten_mon, "khau_phan": b.khau_phan,
                                   "bua": b.bua, "thoi_gian": b.thoi_gian} for b in ket_qua],
            "tong_dinh_duong": tong
        }

    def Luu(self, ten_file="bua_an.json"):
        with open(ten_file, "w", encoding="utf-8") as f:
            json.dump(
                [{"ten_mon": b.ten_mon, "khau_phan": b.khau_phan, "bua": b.bua,
                  "thoi_gian": b.thoi_gian,
                  "dinh_duong": b.tinh_dinh_duong()}
                 for b in self.danh_sach_bua],
                f, ensure_ascii=False, indent=4
            )

    def Doc(self, ten_file="bua_an.json"):
        try:
            with open(ten_file, "r", encoding="utf-8") as f:
                self.danh_sach_bua = [
                    BuaAn(b["ten_mon"], b["khau_phan"], b["bua"], b.get("thoi_gian"))
                    for b in json.load(f)
                ]
            return self.danh_sach_bua
        except FileNotFoundError:
            self.danh_sach_bua = []

            return []

