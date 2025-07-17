def generate_prompt(user_query, products):
    prompt = f"""Bạn là nhân viên tư vấn bán hàng điện thoại, nhiệm vụ của bạn là gợi ý chính xác sản phẩm phù hợp nhu cầu khách. 
        Khách hàng vừa hỏi: "{user_query}"

        Dưới đây là các sản phẩm liên quan tôi tìm được:
        {format_products(products)}

        Hãy phản hồi thật tự nhiên, khéo léo như đang tư vấn trực tiếp, không liệt kê khô cứng.  
        Ưu tiên đưa ra 1-3 lựa chọn phù hợp, mô tả lý do nổi bật.
        Trả lời ngắn gọn, thân thiện."""

    return prompt


def format_products(products):
    return "\n".join(
        [f"- {p['brand_name']} {p['model']} (Camera: {p['primary_camera_rear']}MP, Pin: {p['battery_capacity']}mAh, Giá: {p['price']} VND)" for p in products]
    )



