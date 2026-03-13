import json
import os
from datetime import datetime
from menu import menu

class BuaAn:
    def __init__(self, ten_mon, khau_phan, bua, thoi_gian=None):
        self.ten_mon = ten_mon
        self.khau_phan = khau_phan
        self.bua = bua
        self.thoi_gian = thoi_gian if thoi_gian else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def date(self):
        return self.thoi_gian.split(" ")[0]

    # Trong luulichsu.py -> class BuaAn
    def tinh_dinh_duong(self):
        # Nếu trong JSON đã có sẵn dinh_duong (như file mới bạn gửi)
        if hasattr(self, 'dinh_duong_san_co') and self.dinh_duong_san_co:
            return self.dinh_duong_san_co

        # Nếu không thì tính từ menu
        he_so = self.khau_phan  # Giả sử khau_phan 1.0 là 1 suất
        mon = menu.get(self.ten_mon, {"calo": 0, "protein": 0, "carb": 0, "fat": 0})
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
        self.danh_sach_bua.append(bua_an)

    def Luu(self, ten_file="bua_an.json"):
        try:
            data_to_save = []
            for b in self.danh_sach_bua:
                data_to_save.append({
                    "ten_mon": b.ten_mon,
                    "khau_phan": b.khau_phan,
                    "bua": b.bua,
                    "thoi_gian": b.thoi_gian,
                    "dinh_duong": b.tinh_dinh_duong()
                })
            with open(ten_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")

    def Doc(self, ten_file="bua_an.json"):
        self.danh_sach_bua = []
        # Kiểm tra nếu file không tồn tại hoặc rỗng thì tạo mới mảng rỗng
        if not os.path.exists(ten_file) or os.path.getsize(ten_file) == 0:
            with open(ten_file, "w", encoding="utf-8") as f:
                json.dump([], f)
            return

        try:
            with open(ten_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    bua = BuaAn(
                        item.get("ten_mon"),
                        item.get("khau_phan"),
                        item.get("bua"),
                        item.get("thoi_gian")
                    )
                    self.danh_sach_bua.append(bua)
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")