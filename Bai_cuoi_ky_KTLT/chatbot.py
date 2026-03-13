import requests
import json

class DifyAIService:
    """
    Class quản lý kết nối AI theo hướng OOP.
    Tự động lấy dữ liệu từ đối tượng User và BaoCao.
    """

    def __init__(self, api_key):
        # Điền Key API của bạn vào đây hoặc truyền vào khi khởi tạo
        self.api_key = api_key
        self.url = "https://api.dify.ai/v1/chat-messages"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _lay_ngu_canh_dinh_duong(self, bao_cao_obj):
        """
        Private method: Trích xuất lịch sử ăn uống từ đối tượng BaoCao (baocao.py)
        """
        try:
            # Gọi hàm ThongKeTheoTuan từ thuộc tính lich_su của BaoCao
            thong_ke = bao_cao_obj.lich_su.ThongKeTheoTuan()
            tong = thong_ke.get("tong_dinh_duong", {})

            ngu_canh = (f"Tuần qua: Calo {tong.get('calo', 0)}, "
                        f"Protein {tong.get('protein', 0)}g, "
                        f"Carb {tong.get('carb', 0)}g, "
                        f"Fat {tong.get('fat', 0)}g.")
            return ngu_canh
        except Exception as e:
            return "Chưa có dữ liệu lịch sử ăn uống."

    def get_advice(self, user_obj, bao_cao_obj, question):
        """
        Hàm chính để lấy tư vấn từ AI.
        :param user_obj: Đối tượng thuộc class User (từ login.py)
        :param bao_cao_obj: Đối tượng thuộc class BaoCao (từ baocao.py)
        :param question: Câu hỏi từ giao diện
        """

        # Lấy thông tin người dùng từ login.py
        bmi = round(user_obj.Tinh_BMI(), 2)
        bmr = round(user_obj.Tinh_BMR(), 2)
        muc_tieu = user_obj.aim  # Cân nặng mong muốn

        # Lấy lịch sử từ baocao.py thông qua hàm private ở trên
        history = self._lay_ngu_canh_dinh_duong(bao_cao_obj)

        # Cấu hình dữ liệu gửi sang Dify (khớp với các biến {{user_bmi}}, {{user_aim}})
        payload = {
            "inputs": {
                "user_bmi": str(bmi),
                "user_bmr": str(bmr),
                "user_aim": f"Mục tiêu cân nặng: {muc_tieu}kg",
                "user_history": history
            },
            "query": question,
            "response_mode": "blocking",
            "user": user_obj.name
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            return response.json().get("answer", "AI không có câu trả lời.")
        except Exception as e:
            return f"Lỗi kết nối AI: {str(e)}"


# ________gợi ý giao diện _________
from login import User
from baocao import BaoCao
from chatbot import DifyAIService # Import cái class mình vừa viết ở trên

# --- ĐÂY LÀ NƠI BẠN ĐIỀN KEY API (Key này tui lấy r bà giữ nguyên keys đó là được nha)---
MY_API_KEY = "app-l2b65SsRvG4KvGcMIcRhMqwm" # Dán cái Key bạn lấy trên Dify vào đây

# 1. Khởi tạo người dùng (Dữ liệu từ login.py)
user_hien_tai = User(name="Nam", age=16, gender="Nam", height=1.7, weight=70, aim=65)

# 2. Khởi tạo báo cáo (Dữ liệu từ baocao.py)
bao_cao_hien_tai = BaoCao(user=user_hien_tai)

# 3. Khởi tạo dịch vụ AI với API Key
ai_bot = DifyAIService(api_key=MY_API_KEY)

# 4. Khi người dùng nhấn nút hỏi trên giao diện
cau_hoi = "Với BMI của mình, mình có nên ăn Phở bò buổi sáng không?"
tra_loi = ai_bot.get_advice(user_hien_tai, bao_cao_hien_tai, cau_hoi)

print(tra_loi)