# app.py
import re
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="식단 및 영양 분석", page_icon="🥗", layout="wide")

# -----------------------------
# 1) 음식 데이터베이스 (일부 샘플)
# -----------------------------
FOOD_DB = {
    "밥": {"kcal": 300, "carb": 66, "protein": 6, "fat": 0.6},
    "김치": {"kcal": 10, "carb": 2, "protein": 1, "fat": 0.2},
    "달걀": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "닭가슴살": {"kcal": 165, "carb": 0, "protein": 31, "fat": 3.6},
    "라면": {"kcal": 500, "carb": 77, "protein": 10, "fat": 17},
    "치킨": {"kcal": 430, "carb": 23, "protein": 31, "fat": 24},
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
    # 1) DB에서 찾기
    for key in FOOD_DB:
        if key in food_name:
            return FOOD_DB[key]
    # 2) 카테고리 추정
    for cat in CATEGORY_DEFAULTS:
        if cat in food_name:
            return CATEGORY_DEFAULTS[cat]
    # 3) 못 찾으면 기타
    return CATEGORY_DEFAULTS["기타"]

# -----------------------------
# 3) Streamlit UI
# -----------------------------
st.title("🥗 식단 및 영양 분석")

st.write("하루 동안 먹은 음식을 자유롭게 입력하세요 (예: 아침: 밥, 달걀 2개 / 점심: 라면 1개 / 저녁: 치킨 2조각)")

user_input = st.text_area("식단 입력", height=150)

if st.button("분석하기"):
    foods = re.split(r"[,\n/]", user_input)
    total = {"kcal": 0, "carb": 0, "protein": 0, "fat": 0}
    
    st.subheader("🍽️ 입력된 음식 분석")
    for f in foods:
        f = f.strip()
        if not f: 
            continue
        nutri = estimate_food(f)
        st.write(f"- {f}: {nutri['kcal']} kcal, 탄수 {nutri['carb']}g, 단백질 {nutri['protein']}g, 지방 {nutri['fat']}g")
        for k in total:
            total[k] += nutri[k]
    
    st.subheader("📊 하루 총 섭취량")
    st.write(f"총 칼로리: **{total['kcal']} kcal**")
    st.write(f"탄수화물: **{total['carb']} g**, 단백질: **{total['protein']} g**, 지방: **{total['fat']} g**")

    chart = pd.DataFrame({
        "영양소": ["탄수화물", "단백질", "지방"],
        "g": [total["carb"], total["protein"], total["fat"]]
    })
    st.bar_chart(chart.set_index("영양소"))
