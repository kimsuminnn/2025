import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ✅ API 설정
API_KEY = "YOUR_USDA_API_KEY"
SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
DETAIL_URL = "https://api.nal.usda.gov/fdc/v1/food/"

# ✅ 권장 섭취량 (예시: 성인 기준)
DAILY_RECOMMENDED = {
    "Energy": 2000,  # kcal
    "Protein": 50,   # g
    "Fat": 70,       # g
    "Carbohydrate": 300,  # g
    "Fiber": 25,     # g
    "Calcium": 1000, # mg
    "Iron": 18,      # mg
    "Vitamin C": 90  # mg
}

# ✅ 식품 검색 함수
def search_food(food_name):
    params = {
        "api_key": API_KEY,
        "query": food_name,
        "pageSize": 1
    }
    response = requests.get(SEARCH_URL, params=params)
    data = response.json()
    if data["foods"]:
        return data["foods"][0]["fdcId"]
    return None

# ✅ 영양 정보 가져오기
def get_nutrition(fdc_id):
    response = requests.get(f"{DETAIL_URL}{fdc_id}?api_key={API_KEY}")
    data = response.json()
    nutrients = {}
    for item in data.get("foodNutrients", []):
        name = item["nutrientName"]
        value = item["value"]
        unit = item["unitName"]
        nutrients[name] = (value, unit)
    return nutrients

# ✅ 시각화 함수
def visualize_nutrition(total_nutrients):
    st.subheader("📊 영양소 섭취량 vs 권장량")
    labels = []
    values = []
    recommended = []
    for key in DAILY_RECOMMENDED:
        if key in total_nutrients:
            labels.append(key)
            values.append(total_nutrients[key][0])
            recommended.append(DAILY_RECOMMENDED[key])
    df = pd.DataFrame({
        "섭취량": values,
        "권장량": recommended
    }, index=labels)
    st.bar_chart(df)

# ✅ 개선 팁 함수
def generate_tips(total_nutrients):
    tips = []
    for nutrient, (value, unit) in total_nutrients.items():
        if nutrient in DAILY_RECOMMENDED:
            recommended = DAILY_RECOMMENDED[nutrient]
            if value < recommended * 0.8:
                tips.append(f"🔻 {nutrient} 섭취가 부족해요. {nutrient}이 풍부한 식품을 더 드셔보세요.")
            elif value > recommended * 1.2:
                tips.append(f"🔺 {nutrient} 섭취가 많아요. 과다 섭취를 주의하세요.")
    return tips

# ✅ Streamlit UI
st.title("🥦 식단 및 영양 분석기")
st.write("하루 동안 먹은 음식들을 입력하면 영양소 분석과 식습관 개선 팁을 제공해드려요.")

food_input = st.text_area("🍽️ 오늘 먹은 음식들을 쉼표로 구분해서 입력해주세요", "밥, 김치, 닭가슴살, 바나나")

if st.button("분석 시작"):
    food_list = [f.strip() for f in food_input.split(",")]
    total_nutrients = {}

    with st.spinner("영양소 분석 중..."):
        for food in food_list:
            fdc_id = search_food(food)
            if fdc_id:
                nutrients = get_nutrition(fdc_id)
                for name, (value, unit) in nutrients.items():
                    if name in DAILY_RECOMMENDED:
                        if name not in total_nutrients:
                            total_nutrients[name] = [0, unit]
                        total_nutrients[name][0] += value

    if total_nutrients:
        visualize_nutrition(total_nutrients)
        st.subheader("💡 맞춤형 식습관 개선 팁")
        tips = generate_tips(total_nutrients)
        for tip in tips:
            st.write(tip)
    else:
        st.warning("영양 정보를 찾을 수 없었어요. 음식 이름을 다시 확인해주세요.")
