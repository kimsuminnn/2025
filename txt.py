from difflib import get_close_matches

def estimate_food(food_name: str):
    # 1) 정확히 포함된 음식명 찾기
    for key in FOOD_DB:
        if key in food_name:
            return FOOD_DB[key]

    # 2) 유사한 음식명 찾기
    match = get_close_matches(food_name, FOOD_DB.keys(), n=1, cutoff=0.6)
    if match:
        return FOOD_DB[match[0]]

    # 3) 카테고리 키워드 기반 추정
    category_keywords = {
        "밥": ["밥", "덮밥", "비빔밥", "볶음밥", "오므라이스", "카레"],
        "면": ["면", "라면", "파스타", "우동", "국수"],
        "빵": ["빵", "토스트", "샌드위치", "버거"],
        "고기": ["고기", "소고기", "돼지고기", "치킨", "스테이크"],
        "디저트": ["케이크", "쿠키", "아이스크림", "디저트", "초콜릿"],
    }

    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in food_name:
                return CATEGORY_DEFAULTS[cat]

    # 4) 못 찾으면 기타
    return CATEGORY_DEFAULTS["기타"]
