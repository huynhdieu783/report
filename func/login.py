class User:
    def __init__(self, name: str, age: int, gender: str, height: int, weight: float, aim: str):
        self.name = name
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        self.aim = aim    #cân nặng mong muốn

    def Tinh_BMI(self):
        BMI = self.weight / (self.height ** 2)
        return BMI

    def Tinh_BMR(self):
        height = self.height * 100
        if self.gender == "Nam":
            BMR = (10 * self.weight) + (6.25 * height) - (5 * self.age) + 5
        elif self.gender == "Nữ":
            BMR = (10 * self.weight) + (6.25 * height) - (5 * self.age) - 161
        return BMR

    def Calo_ngay(self):
        hieu = self.weight - self.aim
        calo_min = 0
        calo_max = 0

        if hieu > 0:
            calo_min = 30 * self.weight
            calo_max = 33 * self.weight

        elif hieu < 0:
            calo_min = 22 * self.weight
            calo_max = 25 * self.weight

        elif hieu == 0:
            calo_min = 35 * self.weight
            calo_max = 40 * self.weight

        return calo_min,calo_max

    def Muctieu(self):
        if self.aim > self.weight:
            return f"Mục tiêu của bạn là tăng {self.aim - self.weight}kg"
        elif self.aim < self.weight:
            return f"Mục tiêu của bạn là giảm {self.weight - self.aim}kg"
        else:
            return "Mục tiêu của bạn là duy trì cân nặng"

