import streamlit as st
import pandas as pd

# 음식 DB
FOOD_DB = {
    "밥": {"kcal": 300, "carb": 66, "protein": 6, "fat": 0.6},
    "김치": {"kcal": 10, "carb": 2, "protein": 1, "fat": 0.2},
    "달걀": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란": {"kcal": 70, "carb": 1, "protein": 6, "fat": 5},
    "계란후라이": {"kcal": 90, "carb": 1, "protein": 6, "fat": 7},
    "족발": {"kcal": 350, "carb": 0, "protein": 25, "fat": 25},
    "김": {"kcal": 5, "carb": 0.5, "protein": 0.3, "fat": 0.1},
    "감자": {"kcal": 80, "carb": 18, "protein": 2, "fat": 0.1},
    "떡볶이": {"kcal": 250, "carb": 50, "protein": 4, "fat": 5},
    "과자": {"kcal": 500, "carb": 50, "protein": 5, "fat": 25},
    "젤리": {"kcal": 150, "carb": 35, "protein": 1, "fat": 0},
    "초콜릿": {"kcal": 220, "carb": 25, "protein": 3, "fat": 12},
    "사탕": {"kcal": 50, "carb": 13, "protein": 0, "fat": 0}
}

st.title("🍱 식단 및 영양 분석")

# 세션 상태 초기화
if "foods_input" not in st.session_state:
    st.session_state["foods_input"] = ""
if "user_info" not in st.session_state:
    st.session_state["user_info"] = {"height": None, "weight": None, "goal": None}

# 사용자 정보 입력
st.sidebar.header("👤 내 정보 입력")
height = st.sidebar.number_input("키 (cm)", min_value=100, max_value=250, step=1,
                                 value=st.session_state["user_info"]["height"] or 170)
weight = st.sidebar.number_input("몸무게 (kg)", min_value=30, max_value=200, step=1,
                                 value=st.session_state["user_info"]["weight"] or 60)
goal = st.sidebar.selectbox("목표", ["다이어트", "체중 유지", "벌크업"],
                            index=["다이어트", "체중 유지", "벌크업"].index(
                                st.session_state["user_info"]["goal"] or "체중 유지"))

# 입력값 저장
st.session_state["user_info"] = {"height": height, "weight": weight, "goal": goal}

# 음식 입력창
st.session_state["foods_input"] = st.text_area(
    "오늘 먹은 음식을 입력하세요 (쉼표로 구분)",
    value=st.session_state["foods_input"]
)

foods = [f.strip() for f in st.session_state["foods_input"].split(",") if f.strip()]

# 분석
total = {"kcal": 0, "carb": 0, "protein": 0, "fat": 0}
details = []

for food in foods:
    if food in FOOD_DB:
        data = FOOD_DB[food]
        for k in total:
            total[k] += data[k]
        details.append([food, data["kcal"], data["carb"], data["protein"], data["fat"]])
    else:
        details.append([food, "DB 없음", "-", "-", "-"])

# 결과 표시
if foods:
    st.subheader("📊 영양 분석 결과")
    df = pd.DataFrame(details, columns=["음식", "칼로리", "탄수화물(g)", "단백질(g)", "지방(g)"])
    st.table(df)

    st.write("### 🔎 총 섭취량")
    st.write(f"칼로리: {total['kcal']} kcal")
    st.write(f"탄수화물: {total['carb']} g")
    st.write(f"단백질: {total['protein']} g")
    st.write(f"지방: {total['fat']} g")

    # 맞춤형 팁 제공
    st.write("### 💡 맞춤형 식습관 팁")
    if goal == "다이어트" and total["kcal"] > 2000:
        st.warning("칼로리가 조금 높습니다. 야채 위주의 식단을 추천드려요 🥦")
    elif goal == "벌크업" and total["protein"] < 100:
        st.info("단백질 섭취가 부족합니다. 닭가슴살, 달걀, 두부 등을 추가해보세요 🍗🥚")
    else:
        st.success("좋은 균형 잡힌 식단을 유지하고 있습니다 👍")

    # ✅ Streamlit 내장 차트 활용
    st.write("### 📈 영양소 그래프")
    chart_df = pd.DataFrame(
        {"영양소": list(total.keys()), "섭취량": list(total.values())}
    )
    st.bar_chart(chart_df.set_index("영양소"))

# 🔄 전체 초기화 버튼
if st.button("🔄 내 정보 및 식단 전체 초기화"):
    st.session_state["foods_input"] = ""
    st.session_state["user_info"] = {"height": None, "weight": None, "goal": None}
    st.rerun()
