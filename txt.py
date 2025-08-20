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
# 1) 데이터베이스 (간단 예시용)
# 단위는 1회 제공량(per serving). 실제 값과 다를 수 있음(교육용).
# kcal, carb(g), protein(g), fat(g), fiber(g), sugar(g),
# vit_a(µg RAE), vit_c(mg), calcium(mg), iron(mg), sodium(mg), potassium(mg)
# -----------------------------
def load_food_db() -> pd.DataFrame:
    data = [
        # 한국 일상 식품
        ("밥(백미) 1공기", "공기", 1, 300, 66, 6, 0.6, 1.0, 0.1, 0, 0, 10, 2, 120),
        ("잡곡밥 1공기", "공기", 1, 310, 64, 7, 2.5, 4.5, 1.0, 0, 0, 15, 2.5, 180),
        ("김치 50g", "접시", 1, 10, 2, 1, 0.2, 1.6, 0.5, 8, 9, 40, 0.4, 90),
        ("달걀 1개(50g)", "개", 1, 70, 0.6, 6, 5, 0, 0.2, 75, 0, 28, 0.9, 70),
        ("닭가슴살 100g", "인분", 1, 165, 0, 31, 3.6, 0, 0, 13, 0, 12, 1, 256),
        ("돼지불고기 150g", "인분", 1, 330, 12, 24, 20, 2.0, 7, 15, 0, 40, 2.4, 450),
        ("소불고기 150g", "인분", 1, 340, 15, 23, 20, 1.5, 6, 0, 0, 30, 2.8, 420),
        ("두부 150g", "모", 0.3, 120, 4, 12, 7, 2, 1.5, 0, 0, 250, 2.7, 220),
        ("우유 1컵(200ml)", "컵", 1, 125, 9.6, 6.6, 6.8, 0, 12, 0, 0, 230, 0.1, 370),
        ("요거트 1개(100g)", "개", 1, 60, 8, 3, 2, 0, 2, 2, 0, 110, 0.1, 150),
        ("바나나 1개(100g)", "개", 1, 89, 23, 1.1, 0.3, 2.6, 12, 3, 9, 5, 0.3, 358),
        ("사과 1개(150g)", "개", 1, 80, 21, 0.3, 0.2, 3.6, 16, 3, 5, 10, 0.1, 195),
        ("감귤/오렌지 1개(130g)", "개", 1, 62, 15.5, 1.2, 0.2, 3.1, 12, 70, 40, 0.1, 0.1, 240),
        ("고구마 150g", "개", 1, 180, 42, 3, 0.3, 5.0, 13, 960, 30, 0.8, 72, 700),
        ("시금치나물 100g", "인분", 1, 35, 5, 3, 0.5, 2.4, 0.4, 470, 28, 1.0, 150, 560),
        ("브로콜리 100g", "인분", 1, 34, 7, 3, 0.4, 2.6, 1.7, 31, 47, 0.7, 33, 316),
        ("라면 1개", "개", 1, 500, 77, 10, 17, 4, 3, 0, 0, 30, 5, 250),
        ("김밥 1줄", "줄", 1, 350, 55, 10, 8, 3, 4, 80, 6, 2, 900),
        ("비빔밥 1그릇", "그릇", 1, 550, 80, 18, 15, 6, 9, 200, 15, 4, 1200),
        ("떡볶이 1인분(300g)", "인분", 1, 450, 90, 9, 6, 3, 14, 20, 4, 1.8, 1400),
        ("치킨 2조각", "인분", 1, 430, 23, 31, 24, 1, 3, 40, 0, 25, 2, 350),
        ("햄버거 1개", "개", 1, 500, 45, 25, 26, 3, 7, 80, 1, 200, 4, 350),
        ("피자 1조각", "조각", 1, 285, 33, 12, 11, 2, 3, 80, 2, 180, 2, 180),
        ("콜라 1캔(250ml)", "캔", 1, 105, 26, 0, 0, 0, 26, 0, 0, 0, 15, 0),
        ("물 1컵", "컵", 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ]
    cols = ["food", "unit", "per_unit", "kcal", "carb", "protein", "fat", "fiber",
            "sugar", "vit_a", "vit_c", "calcium", "iron", "sodium", "potassium"]
    df = pd.DataFrame(data, columns=cols)
    return df

FOOD_DB = load_food_db()
FOOD_LOOKUP = {re.sub(r"\s*\(.+?\)", "", row.food).strip(): row for _, row in FOOD_DB.iterrows()}

# -----------------------------
# 2) 17세(고2) 권장량(간이)
# 출처 혼합(국제 가이드라인 기반 교육용 근사치). 실제 처방 용도 아님.
# -----------------------------
AGE = 17

def calorie_target_mifflin(weight_kg: float, height_cm: float, sex: str, activity: str) -> int:
    # Mifflin-St Jeor BMR
    s = 5 if sex == "남" else -161
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * AGE + s
    factor = {"낮음(운동 거의 없음)": 1.35, "보통(주 1-3회)": 1.55, "활발(주 4-6회)": 1.75, "매우 활발(매일 강도 높음)": 1.9}[activity]
    return int(round(bmr * factor))

def rda_table(sex: str) -> Dict[str, float]:
    # 일부 영양소는 성별 차등
    base = {
        "kcal": None,  # 개인별 계산
        "carb": 130,   # g (최소 필요량; 권장 비율은 45-65% kcal)
        "protein": 55 if sex == "남" else 50,  # g (교육용)
        "fat": None,   # 권장 비율 20-35% kcal
        "fiber": 38 if sex == "남" else 26,    # g (AI)
        "sugar": 50,   # g 이하(자유당/WHO 가이드 근사)
        "vit_a": 900 if sex == "남" else 700,  # µg RAE
        "vit_c": 75 if sex == "남" else 65,    # mg
        "calcium": 1300,  # mg
        "iron": 11 if sex == "남" else 15,     # mg
        "sodium": 2300,   # mg (상한)
        "potassium": 4700 # mg (AI)
    }
    return base

# -----------------------------
# 3) 텍스트 입력 파서(간단 규칙)
# 예: "아침: 밥 1공기, 달걀 2개 / 점심: 김밥 1줄, 우유 1컵"
# -----------------------------
def parse_free_text(s: str) -> List[Tuple[str, float]]:
    if not s.strip():
        return []
    # 정규화
    text = s.replace(":", " ").replace("/", ",").replace("\n", ",").replace("·", ",")
    items = re.split(r"[,\u3001]", text)  # 쉼표/일본쉼표
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
            # 가장 유사한 food 찾기(단순 포함 매칭)
            match = None
            for food in FOOD_LOOKUP.keys():
                if food in name or name in food:
                    match = food
                    break
            if match is None:
                # 완전 일치 시도
                if name in FOOD_LOOKUP:
                    match = name
            if match:
                results.append((match, qty))
        else:
            # 수량 미표기 → 1로 가정
            name = it.strip()
            for food in FOOD_LOOKUP.keys():
                if food in name or name in food:
                    results.append((food, 1.0))
                    break
    return results

# -----------------------------
# 4) 합산 및 비교
# -----------------------------
NUTRIENT_KEYS = ["kcal","carb","protein","fat","fiber","sugar","vit_a","vit_c","calcium","iron","sodium","potassium"]

def compute_totals(entries: List[Tuple[str, float]]) -> pd.Series:
    total = pd.Series(0.0, index=NUTRIENT_KEYS)
    expanded_rows = []
    for food, qty in entries:
        row = FOOD_DB[FOOD_DB["food"].str.contains(food)].iloc[0]
        factor = qty / row["per_unit"]  # per serving 대비
        vals = row[NUTRIENT_KEYS] * factor
        total += vals
        expanded_rows.append({
            "food": row["food"], "qty": qty, "kcal": vals["kcal"], "carb": vals["carb"], "protein": vals["protein"],
            "fat": vals["fat"], "fiber": vals["fiber"], "sugar": vals["sugar"], "vit_a": vals["vit_a"],
            "vit_c": vals["vit_c"], "calcium": vals["calcium"], "iron": vals["iron"],
            "sodium": vals["sodium"], "potassium": vals["potassium"]
        })
    detail_df = pd.DataFrame(expanded_rows)
    return total, detail_df

def targets_df(sex: str, weight: float, height: float, activity: str) -> pd.Series:
    r = rda_table(sex)
    kcal_tgt = calorie_target_mifflin(weight, height, sex, activity)
    fat_min = int(0.20 * kcal_tgt / 9)
    fat_max = int(0.35 * kcal_tgt / 9)
    # fat은 범위, carb은 최소, protein은 절대치(교육용)
    tgt = pd.Series({
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
    return tgt

def percent_of_target(total: pd.Series, tgt: pd.Series) -> pd.DataFrame:
    rows = []
    for k in NUTRIENT_KEYS:
        val = total[k]
        if k == "fat":
            lo, hi = tgt[k]
            pct_lo = 100.0 * val / lo if lo else np.nan
            pct_hi = 100.0 * val / hi if hi else np.nan
            status = "적정"
            if val < lo * 0.9: status = "부족"
            elif val > hi * 1.1: status = "과잉"
            rows.append({"nutrient": "지방", "value": val, "target_low": lo, "target_high": hi,
                         "pct_of_low": pct_lo, "pct_of_high": pct_hi, "status": status})
        else:
            target = tgt[k]
            pct = 100.0 * val / target if target else np.nan
            # sodium은 상한 기준 → 100% 초과 시 과잉
            if k == "sodium":
                status = "적정" if val <= target else "과잉"
            else:
                # 85~115% 사이를 적정으로 간주(교육용)
                status = "부족" if pct < 85 else ("과잉" if pct > 115 else "적정")
            rows.append({"nutrient": {
                "kcal":"칼로리","carb":"탄수화물","protein":"단백질","fiber":"식이섬유","sugar":"자유당",
                "vit_a":"비타민 A","vit_c":"비타민 C","calcium":"칼슘","iron":"철","sodium":"나트륨","potassium":"칼륨"
            }[k], "value": val, "target": target, "pct": pct, "status": status})
    return pd.DataFrame(rows)

# -----------------------------
# 5) 개선 팁 생성
# -----------------------------
def tips_generator(pcts: pd.DataFrame) -> List[str]:
    tips = []
    def has(nm, cond):
        rows = pcts[pcts["nutrient"] == nm]
        if rows.empty: return False
        return cond(rows.iloc[0])
    # 단백질
    if has("단백질", lambda r: r["status"]=="부족"):
        tips.append("단백질이 부족해요: 닭가슴살, 달걀, 두부, 생선, 그릭요거트를 한 끼에 1~2단위 추가해보세요.")
    if has("단백질", lambda r: r["status"]=="과잉"):
        tips.append("단백질 과잉 주의: 수분 섭취를 늘리고, 콩/채소로 일부 대체해보세요.")
    # 식이섬유
    if has("식이섬유", lambda r: r["status"]=="부족"):
        tips.append("식이섬유가 부족해요: 과일 1개 + 채소 반접시 + 통곡물(잡곡밥/고구마)을 매 끼니에 추가하세요.")
    # 나트륨
    if has("나트륨", lambda r: r["status"]=="과잉"):
        tips.append("나트륨 과다: 라면/가공식품/국물은 줄이고, 김치·젓갈은 작은 접시만. 물을 충분히 마셔요.")
    # 칼슘/철/비타민
    if has("칼슘", lambda r: r["status"]=="부족"):
        tips.append("칼슘 보강: 우유/요거트 1컵, 두부/멸치/청경채를 자주 섭취해요.")
    if has("철", lambda r: r["status"]=="부족"):
        tips.append("철분 보강: 살코기·간·시금치와 함께 비타민 C 많은 과일(귤/키위)을 같이 먹어요.")
    if has("비타민 C", lambda r: r["status"]=="부족"):
        tips.append("비타민 C 보강: 귤/오렌지/키위/브로콜리를 간식으로.")
    if has("비타민 A", lambda r: r["status"]=="부족"):
        tips.append("비타민 A 보강: 당근/고구마/시금치 같은 주황·녹색 채소를 자주!")
    # 당류
    if has("자유당", lambda r: r["status"]=="과잉"):
        tips.append("당류 과다: 탄산음료·디저트 섭취를 줄이고, 간식은 과일/견과로 교체해요.")
    # 지방
    fat_row = pcts[pcts["nutrient"]=="지방"]
    if not fat_row.empty:
        r = fat_row.iloc[0]
        lo, hi = r["target_low"], r["target_high"]
        if r["value"] < lo*0.9:
            tips.append("지방 너무 적음: 견과류 한 줌, 올리브오일 드레싱으로 건강한 지방을 보충해요.")
        elif r["value"] > hi*1.1:
            tips.append("지방 과다: 튀김/패스트푸드를 줄이고, 구이/찜 조리법을 활용해요.")
    # 수분
    tips.append("수분: 공부/운동 전후로 물을 자주 마시고, 카페인 음료는 늦은 밤 피하세요.")
    return tips

# -----------------------------
# 6) UI
# -----------------------------
st.title("🥗 고2 식단 · 영양 분석기")
st.caption("교육용 도구입니다. 실제 질환/치료 목적의 영양 처방이 아니며, 개인 차이가 있습니다.")

with st.sidebar:
    st.header("📌 사용자 정보")
    sex = st.radio("성별", ["남", "여"], horizontal=True)
    height = st.number_input("키 (cm)", 140, 210, 170)
    weight = st.number_input("몸무게 (kg)", 35.0, 150.0, 60.0, step=0.5)
    activity = st.selectbox("활동 수준", ["낮음(운동 거의 없음)", "보통(주 1-3회)", "활발(주 4-6회)", "매우 활발(매일 강도 높음)"])
    st.markdown("---")
    st.subheader("🔎 식단 입력 방법")
    st.markdown("• 텍스트로: `아침 밥 1공기, 달걀 2개 / 점심 김밥 1줄, 우유 1컵`")
    st.markdown("• 혹은 아래 **선택 입력**에서 음식과 수량을 추가하세요.")

st.subheader("1) 자유 입력")
free_text = st.text_area("오늘 먹은 음식(쉼표/줄바꿈/슬래시로 구분)", height=90, placeholder="예) 아침: 밥 1공기, 달걀 2개 / 점심: 김밥 1줄, 우유 1컵 / 간식: 바나나 1개")

parsed = parse_free_text(free_text)

st.subheader("2) 선택 입력")
col1, col2, col3 = st.columns([2,1,1])
with col1:
    food_sel = st.selectbox("음식 선택", list(FOOD_LOOKUP.keys()))
with col2:
    qty_sel = st.number_input("수량", 0.5, 10.0, 1.0, step=0.5)
with col3:
    add_btn = st.button("추가")

session_entries: List[Tuple[str, float]] = st.session_state.get("entries", [])
if "entries" not in st.session_state:
    st.session_state["entries"] = []

if add_btn:
    session_entries = st.session_state["entries"]
    session_entries.append((food_sel, qty_sel))
    st.session_state["entries"] = session_entries

# 합치기(텍스트 + 선택)
entries = list(parsed) + list(st.session_state["entries"])

st.markdown("#### 📝 오늘의 식단 목록")
if entries:
    disp_df = pd.DataFrame(entries, columns=["음식", "수량"])
    st.dataframe(disp_df, use_container_width=True, hide_index=True)
else:
    st.info("식단을 입력하거나 선택 후 **추가**를 눌러주세요.")

# -----------------------------
# 7) 계산 & 결과
# -----------------------------
if entries:
    total, detail_df = compute_totals(entries)
    tgt = targets_df(sex, weight, height, activity)
    pcts = percent_of_target(total, tgt)

    # 요약 카드
    st.subheader("3) 하루 섭취량 요약")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("총 칼로리(kcal)", f"{int(round(total['kcal']))}")
    k2.metric("탄수화물(g)", f"{round(total['carb'],1)}")
    k3.metric("단백질(g)", f"{round(total['protein'],1)}")
    k4.metric("지방(g)", f"{round(total['fat'],1)}")

    # 세부표
    with st.expander("🍽️ 음식별 기여도(펼치기)"):
        st.dataframe(detail_df.round(2), use_container_width=True)

    # 권장량 정보
    st.subheader("4) 권장 섭취량")
    fat_lo, fat_hi = tgt["fat"]
    tgt_table = pd.DataFrame([
        ["칼로리", f"{tgt['kcal']} kcal"],
        ["탄수화물", f"{tgt['carb']} g 이상(에너지의 45~65%)"],
        ["단백질", f"{tgt['protein']} g"],
        ["지방", f"{fat_lo}~{fat_hi} g (에너지의 20~35%)"],
        ["식이섬유", f"{tgt['fiber']} g"],
        ["자유당(당류)", f"{tgt['sugar']} g 이하"],
        ["비타민 A", f"{tgt['vit_a']} µg RAE"],
        ["비타민 C", f"{tgt['vit_c']} mg"],
        ["칼슘", f"{tgt['calcium']} mg"],
        ["철", f"{tgt['iron']} mg"],
        ["나트륨(상한)", f"{tgt['sodium']} mg 이하"],
        ["칼륨", f"{tgt['potassium']} mg"],
    ], columns=["영양소", "권장량(교육용)"])
    st.table(tgt_table)

    # 시각화 준비
    st.subheader("5) 권장 대비 섭취 비율 시각화")
    # bar chart 데이터(지방 제외, 나트륨은 상한 대비)
    plot_df = pcts.copy()
    plot_df = plot_df[plot_df["nutrient"].isin(["칼로리","탄수화물","단백질","식이섬유","자유당","비타민 A","비타민 C","칼슘","철","나트륨","칼륨"])]
    plot_df["pct_clipped"] = plot_df["pct"].clip(0, 200)  # 200% 상한으로 잘라 표시
    plot_df["라벨"] = plot_df["pct"].apply(lambda x: f"{int(round(x))}%" if pd.notnull(x) else "-")
    plot_df["상태"] = plot_df["status"]

    bar = alt.Chart(plot_df).mark_bar().encode(
        x=alt.X("pct_clipped:Q", title="권장 대비 (%)", axis=alt.Axis(format="~s")),
        y=alt.Y("nutrient:N", title=None, sort="-x"),
        tooltip=["nutrient","value","target","pct","status"],
        color=alt.Color("상태:N", scale=alt.Scale(domain=["부족","적정","과잉"]))
    ).properties(height=380, use_container_width=True)
    rule = alt.Chart(pd.DataFrame({'x':[100]})).mark_rule(strokeDash=[4,4]).encode(x='x:Q')
    st.altair_chart(bar + rule, use_container_width=True)

    # 지방 범위 시각화(특수)
    st.markdown("**지방(g) 범위 비교**")
    fat_val = pcts[pcts["nutrient"]=="지방"].iloc[0]["value"]
    fat_low, fat_high = int(tgt["fat"][0]), int(tgt["fat"][1])
    fat_df = pd.DataFrame({"항목":["지방 섭취","권장 하한","권장 상한"], "g":[fat_val, fat_low, fat_high]})
    fat_chart = alt.Chart(fat_df).mark_bar().encode(
        x=alt.X("g:Q", title="g"),
        y=alt.Y("항목:N", title=None),
        tooltip=["항목","g"]
    )
    st.altair_chart(fat_chart, use_container_width=True)

    # 개선 팁
    st.subheader("6) 맞춤형 식습관 개선 팁")
    tips = tips_generator(pcts)
    for t in tips:
        st.write("• " + t)

    # 보고서/다운로드
    st.subheader("7) 결과 내보내기")
    report = {
        "user": {"sex": sex, "age": AGE, "height_cm": height, "weight_kg": weight, "activity": activity},
        "target": tgt.apply(lambda x: (float(x[0]), float(x[1])) if isinstance(x, tuple) else float(x) if x is not None else None).to_dict(),
        "total": total.round(2).to_dict(),
        "assessment": pcts.to_dict(orient="records"),
        "entries": [{"food": f, "qty": float(q)} for f, q in entries],
    }
    st.download_button("📥 JSON 다운로드", data=json.dumps(report, ensure_ascii=False, indent=2), file_name="diet_report.json")
    csv = detail_df.round(2).to_csv(index=False)
    st.download_button("📥 음식별 영양 CSV", data=csv, file_name="diet_details.csv")

else:
    st.stop()

# 하단 도움말
st.markdown("---")
st.caption("※ 수치는 교육용 근사치입니다. 알레르기/질환이 있거나 체중 조절이 필요하면 전문가와 상담하세요.")
