# app.py
# -*- coding: utf-8 -*-
import re
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="식단 및 영양 분석", page_icon="🥗", layout="wide")

# -----------------------------
# 1) 음식 데이터베이스
# -----------------------------
FOOD_DB = {
    "밥": {"kcal": 300, "carb": 66, "protein": 6, "fat": 0.6},
    "김치": {"kcal": 10, "carb": 2, "protein": 1, "fat": 0.2},
    "달걀": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란후라이": {"kcal": 90, "carb": 1, "protein": 6, "fat": 7},
    "닭가슴살": {"kcal": 165, "carb": 0, "protein": 31, "fat": 3.6},
    "라면": {"kcal": 500, "carb": 77, "protein": 10, "fat": 17},
    "치킨": {"kcal": 215, "carb": 12, "protein": 15, "fat": 12},
    "족발": {"kcal": 350, "carb": 0, "protein": 25, "fat": 25},
    "김": {"kcal": 5, "carb": 0.5, "protein": 0.3, "fat": 0.1},
    "감자": {"kcal": 80, "carb": 18, "protein": 2, "fat": 0.1},
    "떡볶이": {"kcal": 250, "carb": 50, "protein": 4, "fat": 5},
    "과자": {"kcal": 500, "carb": 50, "protein": 5, "fat": 25},
    "젤리": {"kcal": 150, "carb": 35, "protein": 1, "fat": 0},
    "초콜릿": {"kcal": 220, "carb": 25, "protein": 3, "fat": 12},
    "사탕": {"kcal": 50, "carb": 13, "protein": 0, "fat": 0}
}

# -----------------------------
# 2) 없는 음식 → 카테고리별 추정치
# -----------------------------
CATEGORY_DEFAULTS = {
    "밥": {"kcal": 300, "carb": 65, "protein": 6, "fat": 1},
    "면": {"kcal": 400, "carb": 75, "protein": 12, "fat": 8},
    "빵": {"kcal": 250, "carb": 45, "protein": 7, "fat": 5},
    "고기": {"kcal": 350, "carb": 5, "protein": 25, "fat": 20},
    "디저트": {"kcal": 280, "carb": 40, "protein": 4, "fat": 10},
    "기타": {"kcal": 200, "carb": 30, "protein": 5, "fat": 5},
}

def estimate_food(food_name: str):
    for key in FOOD_DB:
        if key in food_name:
            return FOOD_DB[key]
    for cat in CATEGORY_DEFAULTS:
        if cat in food_name:
            return CATEGORY_DEFAULTS[cat]
    return CATEGORY_DEFAULTS["기타"]

# -----------------------------
# 3) 권장 칼로리 및 영양소 계산
# -----------------------------
def calc_recommendations(sex, age, weight, height, activity):
    if sex == "남":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_factor = {"낮음": 1.2, "보통": 1.55, "높음": 1.725}[activity]
    tdee = int(bmr * activity_factor)

    carb = int((0.55 * tdee) / 4)
    protein = int((0.20 * tdee) / 4)
    fat = int((0.25 * tdee) / 9)
    return {"kcal": tdee, "carb": carb, "protein": protein, "fat": fat}

# -----------------------------
# 4) 맞춤형 팁 생성
# -----------------------------
def generate_tips(total, rec):
    tips = []
    if total["kcal"] < rec["kcal"] * 0.9:
        tips.append("칼로리가 부족해요. 밥, 감자, 고구마 같은 탄수화물 음식을 조금 더 드세요.")
    elif total["kcal"] > rec["kcal"] * 1.1:
        tips.append("칼로리가 과해요. 간식이나 튀긴 음식 섭취를 줄이는 게 좋아요.")
    if total["protein"] < rec["protein"] * 0.9:
        tips.append("단백질이 부족해요. 달걀, 두부, 닭가슴살 같은 단백질 식품을 더 드세요.")
    elif total["protein"] > rec["protein"] * 1.2:
        tips.append("단백질이 과해요. 과한 단백질은 신장에 부담을 줄 수 있어요.")
    if total["carb"] < rec["carb"] * 0.9:
        tips.append("탄수화물이 부족해요. 밥, 빵, 과일을 추가해 보세요.")
    elif total["carb"] > rec["carb"] * 1.2:
        tips.append("탄수화물이 많아요. 단 음료나 과자를 줄이는 게 좋아요.")
    if total["fat"] < rec["fat"] * 0.8:
        tips.append("지방이 부족해요. 견과류나 올리브유 같은 건강한 지방을 섭취해 보세요.")
    elif total["fat"] > rec["fat"] * 1.2:
        tips.append("지방 섭취가 많아요. 튀김류보다는 구이나 찜을 선택하세요.")
    if not tips:
        tips.append("아주 균형 잡힌 식단이에요! 👏 계속 유지해 보세요.")
    return tips

# -----------------------------
# 5) Streamlit UI
# -----------------------------
st.title("🥗 식단 및 영양 분석")

st.subheader("👤 내 정보 입력")
col1, col2, col3 = st.columns(3)
with col1:
    sex = st.radio("성별", ["남", "여"])
with col2:
    age = st.number_input("나이", 5, 100, 20)
with col3:
    activity = st.selectbox("활동량", ["낮음", "보통", "높음"])

col4, col5 = st.columns(2)
with col4:
    height = st.number_input("키(cm)", 100, 220, 170)
with col5:
    weight = st.number_input("몸무게(kg)", 20, 200, 60)

st.write("---")
st.subheader("🍽️ 식단 입력")
st.write("예시: 아침: 밥, 달걀 2개 / 점심: 라면 1개 / 저녁: 치킨 2조각")
user_input = st.text_area("하루 동안 먹은 음식", height=150)

if st.button("분석하기"):
    rec = calc_recommendations(sex, age, weight, height, activity)
    foods = re.split(r"[,\n/]", user_input)
    total = {"kcal": 0, "carb": 0, "protein": 0, "fat": 0}

    st.subheader("🍱 입력된 음식 분석")
    for f in foods:
        f = f.strip()
        if not f:
            continue
        nutri = estimate_food(f)
        st.write(f"- {f}: {nutri['kcal']} kcal, 탄수 {nutri['carb']}g, 단백질 {nutri['protein']}g, 지방 {nutri['fat']}g")
        for k in total:
            total[k] += nutri[k]

    st.subheader("📊 하루 총 섭취량 vs 권장량")
    st.write(f"**총 칼로리:** {total['kcal']} kcal / 권장 {rec['kcal']} kcal")
    st.write(f"**탄수화물:** {total['carb']} g / 권장 {rec['carb']} g")
    st.write(f"**단백질:** {total['protein']} g / 권장 {rec['protein']} g")
    st.write(f"**지방:** {total['fat']} g / 권장 {rec['fat']} g")

    # -----------------------------
    # 그룹드 바 차트 (탄단지 나란히)
    # -----------------------------
    chart = pd.DataFrame({
        "영양소": ["탄수화물", "단백질", "지방"],
        "섭취량": [total["carb"], total["protein"], total["fat"]],
        "권장량": [rec["carb"], rec["protein"], rec["fat"]]
    })
    chart_melt = chart.melt("영양소", var_name="구분", value_name="g")

    bar = (
        alt.Chart(chart_melt)
        .mark_bar()
        .encode(
            x=alt.X("영양소:N", title="영양소"),
            y=alt.Y("g:Q", title="g (그램)"),
            color=alt.Color("구분:N", scale=alt.Scale(scheme="set2")),
            xOffset="구분:N"
        )
        .properties(width=600, height=400)
    )

    text = (
        alt.Chart(chart_melt)
        .mark_text(dy=-5)
        .encode(
            x=alt.X("영양소:N"),
            y="g:Q",
            text="g:Q",
            xOffset="구분:N",
            color=alt.Color("구분:N")
        )
    )

    st.altair_chart(bar + text, use_container_width=True)

    st.subheader("💡 맞춤형 식습관 개선 팁")
    tips = generate_tips(total, rec)
    for t in tips:
        st.write("- " + t)
