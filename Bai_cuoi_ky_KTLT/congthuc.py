

from menu import menu

class MonAn:
    def __init__(self, key, data):
        self.key = key
        self.ten = data.get("ten", "")
        self.calo = data.get("calo", 0)
        self.protein = data.get("protein", 0)
        self.carb = data.get("carb", 0)
        self.fat = data.get("fat", 0)
        self.fiber = data.get("fiber", 0)
        self.cong_thuc = data.get("congthuc", "")

class TimKiemCongThuc:
    def __init__(self):
        self.danh_sach_mon = [MonAn(k, v) for k, v in menu.items()]

    def tim_theo_ten(self, ten_tim):
        ten_tim = ten_tim.lower().strip()
        return [mon for mon in self.danh_sach_mon if ten_tim in mon.ten.lower()]

    def tim_theo_calo(self, calo_min, calo_max):
        return [mon for mon in self.danh_sach_mon if calo_min <= mon.calo <= calo_max]

    def tim_theo_nguyen_lieu(self, danh_sach_nl):
        if not danh_sach_nl:
            return []
        ket_qua = []
        for mon in self.danh_sach_mon:
            for nl in danh_sach_nl:
                if nl.lower().strip() in mon.cong_thuc.lower():
                    ket_qua.append(mon)
                    break
        return ket_qua

if __name__ == "__main__":
    ql = TimKiemCongThuc()

    print("=" * 60)
    print("      CHƯƠNG TRÌNH TÌM KIẾM CÔNG THỨC NẤU ĂN")
    print("=" * 60)

    # Hướng 1: Tìm theo tên
    print("\n[1] Tìm theo tên 'bún':")
    ql.hien_thi(ql.tim_theo_ten("bún"))

    # Hướng 2: Tìm theo calo
    print("\n[2] Tìm theo calo (200 - 350):")
    ql.hien_thi(ql.tim_theo_calo(200, 350))

    # Hướng 3: Tìm theo nguyên liệu
    print("\n[3] Tìm theo nguyên liệu ['tôm', 'cà chua']:")
    ql.hien_thi(ql.tim_theo_nguyen_lieu(["tôm", "cà chua"]))