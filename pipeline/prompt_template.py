def generate_prompt(query: str, products: list):
    top_n = 3  # Chỉ lấy top 3 sản phẩm nổi bật
    prompt = f"Người dùng hỏi: {query}\n\n"
    prompt += "Dưới đây là một số sản phẩm liên quan:\n"

    for p in products[:top_n]:
        prompt += f"- {p['model']} ({p['price']} VND): {p['primary_camera_rear']}MP camera, {p['battery_capacity']}mAh battery, {p['ram_capacity']}GB RAM\n"

    prompt += "\nHãy đề xuất sản phẩm phù hợp nhất và nêu lý do chọn lựa."
    return prompt


