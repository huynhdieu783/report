
from menu import menu

class TimKiem:
    def __init__(self, monan):
        self.monan = monan
        self.menu = menu

    def dichmon(self, text):
        mon_an = text.lower().replace(" ", "")
        inputs = "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
        outputs = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
        dich = mon_an.maketrans(inputs, outputs)
        return mon_an.translate(dich)


    def tim_kiem_mon_an(self):
        ten_mon = self.dichmon(self.monan)
        if ten_mon in self.menu:
            return self.menu[ten_mon]  #muốn lấy thành phần nào thi .get("") thành phần đó ra nha
        else:
            return False


if __name__ == "__main__":
    timkiem = TimKiem("phở bò")
    print(timkiem.tim_kiem_mon_an().get("congthuc"))