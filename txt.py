# app.py
# -*- coding: utf-8 -*-
import re
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="식단 및 영양 분석", page_icon="🥗", layout="wide")

# -----------------------------
# 1) 음식 데이터베이스 (샘플)
# -----------------------------
FOOD_DB = {
    "밥": {"kcal": 300, "carb": 66, "protein": 6, "fat": 0.6},
    "김치": {"kcal": 10, "carb": 2, "protein": 1, "fat": 0.2},
    "달걀": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란후라이": {"kcal": 90, "carb": 1, "protein": 6, "fat": 7},
    "닭가슴살": {"kcal": 165, "carb": 0, "protein": 31, "fat": 3.6},
    "라면": {"kcal": 500, "carb": 77, "protein": 10, "fat": 17},
    "치킨": {"kcal": 430, "carb": 23, "protein": 31, "fat": 24},
    "과자": {"kcal": 500, "carb": 50, "protein": 5, "fat": 25},
    "젤리": {"kcal": 150, "carb": 35, "protein": 1, "fat": 0},
    "초콜릿": {"kcal": 220, "carb": 25, "protein": 3, "fat": 12},
    "사탕": {"kcal": 50, "carb": 13, "protein": 0, "fat": 0},
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

# ---------------------------
