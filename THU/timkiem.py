def trans(text):
    text = text.lower()
    inputs = "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
    outputs = "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
    dich = text.maketrans(inputs, outputs)
    return text.translate(dich)
noi_dung = input("Nhập chuỗi tiếng Việt có dấu: ")
ket_qua = trans(noi_dung)
print(f"Kết quả sau khi chuyển đổi: {ket_qua}")