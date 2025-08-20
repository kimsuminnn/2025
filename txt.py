import streamlit as st
import pandas as pd

st.title("🥗 식단 및 영양 분석기")
st.write("하루 식단을 입력하면 칼로리와 영양소를 분석하고 개선 팁을 제공해요.")

# 사용자 입력
st.subheader("🍽️ 오늘 먹은 음식과 영양 정보 입력")
food_data = st.text_area("음식 이름, 칼로리(kcal), 탄수화물(g), 단백질(g), 지방(g)을 쉼표로 구분해 입력하세요.\n예: 바나나, 90, 23, 1, 0.3\n여러 줄로 입력 가능", height=200)

# 권장 섭취량 (성인 기준)
recommended = {
    "칼로리": 2000,
    "탄수화물": 300,
    "단백질": 50,
    "지방": 70
}

if st.button("분석하기"):
    lines = food_data.strip().split("\n")
    total = {"칼로리": 0, "탄수화물": 0, "단백질": 0, "지방": 0}
    food_list = []

    for line in lines:
        try:
            name, cal, carb, protein, fat = [x.strip() for x in line.split(",")]
            cal, carb, protein, fat = float(cal), float(carb), float(protein), float(fat)
            total["칼로리"] += cal
            total["탄수화물"] += carb
            total["단백질"] += protein
            total["지방"] += fat
            food_list.append({
                "음식": name,
                "칼로리": cal,
                "탄수화물": carb,
                "단백질": protein,
                "지방": fat
            })
        except:
            st.error(f"입력 오류: '{line}' 형식을 확인해주세요.")

    # 결과 출력
    st.subheader("📊 섭취 요약")
    df = pd.DataFrame(food_list)
    st.dataframe(df)

    st.subheader("📈 총 섭취량 vs 권장량")
    compare_df = pd.DataFrame({
        "섭취량": [total[k] for k in recommended],
        "권장량": [recommended[k] for k in recommended]
    }, index=recommended.keys())
    st.bar_chart(compare_df)

    # 개선 팁
    st.subheader("💡 식습관 개선 팁")
    for key in recommended:
        intake = total[key]
        need = recommended[key]
        if intake < need * 0.8:
            st.write(f"🔻 {key} 섭취가 부족해요. {key}이 풍부한 식품을 더 드셔보세요.")
        elif intake > need * 1.2:
            st.write(f"🔺 {key} 섭취가 많아요. 과다 섭취를 주의하세요.")
        else:
            st.write(f"✅ {key} 섭취가 적절해요. 잘하고 있어요!")

