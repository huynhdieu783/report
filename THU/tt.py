import json

# Dữ liệu nhập vào
data = {
    "students": [
        {
            "name": input("Tên: "),
            "age": input("Tuổi: "),
            "email": input("Email: ")
        }
    ]
}

# Lưu vào file JSON
with open("students.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Đã lưu!")
