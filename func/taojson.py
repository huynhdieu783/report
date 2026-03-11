import json

data = {
    "name": "Nutri-Gen AI",
    "version": "1.0",
    "features": ["Personalized meal plans", "AI Chatbot"],
    "active": True
}

with open("data_nutri.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)