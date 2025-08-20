# app.py
# -*- coding: utf-8 -*-
import re
import json
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="고2 식단 · 영양 분석기", page_icon="🥗", layout="wide")

# -----------------------------
# 1) 음식 데이터베이스 (15개 열 맞춤)
# -----------------------------
def load_food_db() -> pd.DataFrame:
    data = [
        # food, unit, per_unit, kcal, carb, protein, fat, fiber,
        # sugar, vit_a, vit_c, calcium, iron, sodium, potassium
        ("밥(백미) 1공기", "공기", 1, 300, 66, 6, 0.6, 1.0, 0.1, 0, 0, 10, 2, 120, 26),
        ("잡곡밥 1공기", "공기", 1, 310, 64, 7, 2.5, 4.5, 1.0, 0, 0, 15, 2.5, 180, 30),
        ("김치 50g", "접시", 1, 10, 2, 1, 0.2, 1.6, 0.5, 8, 9, 40, 0.4, 300, 90),
        ("달걀 1개(50g)", "개", 1, 70, 0.6, 6, 5, 0, 0.2, 75, 0, 28, 0.9, 60, 70),
        ("닭가슴살 100g", "인분", 1, 165, 0, 31, 3.6, 0, 0, 13, 0, 12, 1, 70, 256),
        ("돼지불고기 150g", "인분", 1, 330, 12, 24, 20, 2.0, 7, 15, 0, 40, 2.4, 600, 450),
        ("소불고기 150g", "인분", 1, 340, 15, 23, 20, 1.5, 6, 0, 0, 30, 2.8, 550, 420),
        ("두부 150g", "모", 1, 120, 4, 12, 7, 2, 1.5, 0, 0, 250, 2.7, 5, 220),
        ("우유 1컵(200ml)", "컵", 1, 125, 9.6, 6.6, 6.8, 0, 12, 0, 0, 230, 0.1, 100, 370),
        ("요거트 1개(100g)", "개", 1, 60, 8, 3, 2, 0, 2, 2, 0, 110, 0.1, 50, 150),
        ("바나나 1개(100g)", "개", 1, 89, 23, 1.1, 0.3, 2.6, 12, 3, 9, 5, 0.3, 1, 358),
        ("사과 1개(150g)", "개", 1, 80, 21, 0.3, 0.2, 3.6, 16, 3, 5, 10, 0.1, 1, 195),
        ("감귤/오렌지 1개(130g)", "개", 1, 62, 15.5, 1.2, 0.2, 3.1, 12, 70, 40, 50, 0.1, 1, 240),
        ("고구마 150g", "개", 1, 180, 42, 3, 0.3, 5.0, 13, 960, 30, 40, 0.8, 20, 700),
        ("시금치나물 100g", "인분", 1, 35, 5, 3, 0.5, 2.4, 0.4, 470, 28, 90, 1.0, 150, 560),
        ("브로콜리 100g", "인분", 1, 34, 7, 3, 0.4, 2.6, 1.7, 31, 47, 50, 0.7, 33, 316),
        ("라면 1개", "개", 1, 500, 77, 10, 17, 4, 3, 0, 0, 30, 5, 1700, 250),
        ("김밥 1줄", "줄", 1, 350, 55, 10, 8, 3, 4, 80, 6, 50, 2, 900, 200),
        ("비빔밥 1그릇", "그릇", 1, 550, 80, 18, 15, 6, 9, 200, 15, 80, 4, 1200, 400),
        ("떡볶이 1인분(300g)", "인분", 1, 450, 90, 9, 6, 3, 14, 20, 4, 60, 1.8, 1400, 300),
        ("치킨 2조각", "인분", 1, 430, 23, 31, 24, 1, 3, 40, 0, 25, 2, 350, 300),
        ("햄버거 1개", "개", 1, 500, 45, 25, 26, 3, 7, 80, 1, 200, 4, 700, 350),
        ("피자 1조각", "조각", 1, 285, 33, 12, 11, 2, 3, 80, 2, 180, 2, 600, 180),
        ("콜라 1캔(250ml)", "캔", 1, 105, 26, 0, 0, 0, 26, 0, 0, 0, 0, 15, 0),
        ("물 1컵", "컵", 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ]
    cols = ["food", "unit", "per_unit", "kcal", "carb", "protein", "fat", "fiber",
            "sugar", "vit_a", "vit_c", "calcium", "iron", "sodium", "potassium"]
    return pd.DataFrame(data, columns=cols)

FOOD_DB = load_food_db()
FOOD_LOOKUP = {re.sub(r"\s*\(.+?\)", "", row.food).strip(): row for _, row in FOOD_DB.iterrows()}

# -----------------------------
# 2) 권장 섭취량 함수 (17세 기준)
# -----------------------------
AGE = 17

def calorie_target_mifflin(weight_kg: float, height_cm: float, sex: str, activity: str) -> int:
    s = 5 if sex == "남" else -161
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * AGE + s
    factor = {"낮음(운동 거의 없음)": 1.35, "보통(주 1-3회)": 1.55,
              "활발(주 4-6회)": 1.75, "매우 활발(매일 강도 높음)": 1.9}[activity]
    return int(round(bmr * factor))

def rda_table(sex: str) -> Dict[str, float]:
    return {
        "kcal": None,
        "carb": 130,
        "protein": 55 if sex == "남" else 50,
        "fat": None,
        "fiber": 38 if sex == "남" else 26,
        "sugar": 50,
        "vit_a": 900 if sex == "남" else 700,
        "vit_c": 75 if sex == "남" else 65,
        "calcium": 1300,
        "iron": 11 if sex == "남" else 15,
        "sodium": 2300,
        "potassium": 4700,
    }

# -----------------------------
# 3) 텍스트 입력 파서
# -----------------------------
def parse_free_text(s: str) -> List[Tuple[str, float]]:
    if not s.strip():
        return []
    text = s.replace(":", " ").replace("/", ",").replace("\n", ",").replace("·", ",")
    items = re.split(r"[,\u3001]", text)
    results = []
    pattern_qty = re.compile(r"(?P<name>[\w가-힣\s]+?)\s*(?P<qty>\d+(\.\d+)?)\s*(?P<unit>개|공기|컵|인분|줄|조각|캔|모)?")
    for it in items:
        it = it.strip()
        if not it:
            continue
        m = pattern_qty.search(it)
        if m:
            name = m.group("name").strip()
            qty = float(m.group("qty"))
            match = None
            for food in FOOD_LOOKUP.keys():
                if food in name or name in food:
                    match = food
                    break
            if match:
                results.append((match, qty))
        else:
            name = it.strip()
            for food in FOOD_LOOKUP.keys():
                if food in name or name in food:
                    results.append((food, 1.0))
                    break
    return results

# -----------------------------
# 4) 합산 및 비교 함수
# -----------------------------
NUTRIENT_KEYS = ["kcal","carb","protein","fat","fiber","sugar",
                 "vit_a","vit_c","calcium","iron","sodium","potassium"]

def compute_totals(entries: List[Tuple[str, float]]) -> pd.Series:
    total = pd.Series(0.0, index=NUTRIENT_KEYS)
    expanded_rows = []
    for food, qty in entries:
        row = FOOD_DB[FOOD_DB["food"].str.contains(food)].iloc[0]
        factor = qty / row["per_unit"]
        vals = row[NUTRIENT_KEYS] * factor
        total += vals
        expanded_rows.append({"food": row["food"], "qty": qty, **vals.to_dict()})
    return total, pd.DataFrame(expanded_rows)

def targets_df(sex: str, weight: float, height: float, activity: str) -> pd.Series:
    r = rda_table(sex)
    kcal_tgt = calorie_target_mifflin(weight, height, sex, activity)
    fat_min = int(0.20 * kcal_tgt / 9)
    fat_max = int(0.35 * kcal_tgt / 9)
    return pd.Series({
        "kcal": kcal_tgt,
        "carb": r["carb"],
        "protein": r["protein"],
        "fat": (fat_min, fat_max),
        "fiber": r["fiber"],
        "sugar": r["sugar"],
        "vit_a": r["vit_a"],
        "vit_c": r["vit_c"],
        "calcium": r["calcium"],
        "iron": r["iron"],
        "sodium": r["sodium"],
        "potassium": r["potassium"],
    })

def percent_of_target(total: pd.Series, tgt: pd.Series) -> pd.DataFrame:
    rows = []
    for k in NUTRIENT_KEYS:
        val = total[k]
        if k == "fat":
            lo, hi = tgt[k]
            status = "적정"
            if val < lo * 0.9: status = "부족"
            elif val > hi * 1.1: status = "과잉"
            rows.append({"nutrient": "지방","value":val,"target_low":lo,"target_high":hi,"status":status})
        else:
            target = tgt[k]
            pct = 100.0 * val / target if target else np.nan
            if k == "sodium":
                status = "적정" if val <= target else "과잉"
            else:
                status = "부족" if pct < 85 else ("과잉" if pct > 115 else "적정")
            rows.append({"nutrient": {
                "kcal":"칼로리","carb":"탄수화물","protein":"단백질","fiber":"식이섬유",
                "sugar":"자유당","vit_a":"비타민 A","vit_c":"비타민 C","calcium":"칼슘",
                "iron":"철","sodium":"나트륨","potassium":"칼륨"}[k],
                "value": val, "target": target, "pct": pct, "status": status})
    return pd.DataFrame(rows)

# -----------------------------
# 5) 개선 팁
# -----------------------------
def tips_generator(pcts: pd.DataFrame) -> List[str]:
    tips = []
    def has(nm, cond):
        rows = pcts[pcts["nutrient"] == nm]
        return (not rows.empty) and cond(rows.iloc[0])
    if has("단백질", lambda r: r["status"]=="부족"):
        tips.append("단백질이 부족해요: 닭가슴살, 달걀, 두부, 생선을 추가하세요.")
    if has("단백질", lambda r: r["status"]=="과잉"):
        tips.append("단백질 과잉: 수분 섭취 늘리고 일부는 채소/곡물로 대체해요.")
    if has("식이섬유", lambda r: r["status"]=="부족"):
        tips.append("식이섬유 부족: 과일 1개, 채소 반 접시를 추가하세요.")
    if has("나트륨", lambda r: r["status"]=="과잉"):
        tips.append("나트륨 과다: 라면/국물 줄이고 물을 충분히 마셔요.")
    if has("칼슘", lambda r: r["status"]=="부족"):
        tips.append("칼슘 보강: 우유, 두부, 멸치를 섭취해요.")
    if has("철", lambda r: r["status"]=="부족"):
        tips.append("철분 보강: 살코기+비타민 C 과일을 함께 드세요.")
    if has("비타민 C", lambda r: r["status"]=="부족"):
        tips.append("비타민 C 부족: 귤/오렌지를 간식으로.")
    if has("비타민 A", lambda r: r["status"]=="부족"):
        tips.append("비타민 A 부족: 당근, 시금치 같은 채소를 드세요.")
    if has("자유당", lambda r: r["status"]=="과잉"):
        tips.append("당류 과다: 탄산음료 대신 과일을 드세요.")
    tips.append("수분: 하루 6~8컵 물을 자주 마셔요.")
    return tips

# -----------------------------
# 6) Streamlit UI
# -----------------------------
st.title("🥗 고2 식단 · 영양 분석기")
st.caption("교육용 도구입니다. 실제 치료/진단용이 아닙니다.")

with st.sidebar:
    st.header("📌 사용자 정보")
    sex = st.radio("성별", ["남", "여"], horizontal=True)
    height = st.number_input("키 (cm)", 140, 210, 170)
    weight = st.number_input("몸무게 (kg)", 35.0, 150.0, 60.0, step=0.5)
    activity = st.selectbox("활동 수준", ["낮음(운동 거의 없음)", "보통(주 1-3회)", "활발(주 4-6회)", "매우 활발(매일 강도 높음)"])

st.subheader("1) 자유 입력")
free_text = st.text_area("오늘 먹은 음식", height=80,
    placeholder="예) 아침: 밥 1공기, 달걀 2개 / 점심: 김밥 1줄, 우유 1컵")

parsed = parse_free_text(free_text)

st.subheader("2) 선택 입력")
col1, col2, col3 = st.columns([2,1,1])
with col1: food_sel = st.selectbox("음식 선택", list(FOOD_LOOKUP.keys()))
with col2: qty_sel = st.number_input("수량", 0.5, 10.0, 1.0, step=0.5)
with col3: add_btn = st.button("추가")

if "entries" not in st.session_state: st.session_state["entries"] = []
if add_btn: st.session_state["entries"].append((food_sel, qty_sel))

entries = list(parsed) + st.session_state["entries"]

st.markdown("#### 📝 오늘의 식단 목록")
if entries:
    st.dataframe(pd.DataFrame(entries, columns=["음식","수량"]), use_container_width=True, hide_index=True)
else:
    st.info("식단을 입력하거나 선택 후 추가해주세요.")

# -----------------------------
# 7) 결과 계산
# -----------------------------
if entries:
    total, detail_df = compute_totals(entries)
