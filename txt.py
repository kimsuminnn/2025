import streamlit as st
import pandas as pd

st.title("🍽️ 자동 칼로리 및 영양소 분석기")
st.write("음식 이름만 입력하면 칼로리와 영양소를 자동으로 계산해드려요!")

# ✅ 음식-영양소 데이터셋 (예시)
food_db = {
    "밥": {"칼로리": 300, "탄수화물": 65, "단백질": 6, "지방": 0.5},
    "김치": {"칼로리": 30, "탄수화물": 7, "단백질": 2, "지방": 0.2},
    "닭가슴살": {"칼로리": 165, "탄수화물": 0, "단백질": 31, "지방": 3.6},
    "바나나": {"칼로리": 90, "탄수화물": 23, "단백질": 1, "지방": 0.3},
    "계란": {"칼로리": 70, "탄수화물": 0.6, "단백질": 6, "지방": 5},
    "사과": {"칼로리": 52, "탄수화물": 14, "단백질": 0.3, "지방": 0.2},
    "우유": {"칼로리": 100, "탄수화물": 12, "단백질": 8, "지방": 4.5},
    "고구마": {"칼로리": 130, "탄수화물": 30, "단백질": 2, "지방": 0.1}
}

# ✅ 권장 섭취량 (성인 기준)
recommended = {
    "칼로리": 2000,
    "탄수화물": 300,
    "단백질": 50,
    "지방": 70
}

# ✅ 사용자 입력
st.subheader("📝 오늘 먹은 음식 입력")
food_input = st.text_area("쉼표로 구분해서 입력해주세요 (예: 밥, 김치, 닭가슴살)", height=100)

if st.button("분석 시작"):
    food_list = [f.strip() for f in food_input.split(",")]
    total = {"칼로리": 0, "탄수화물": 0, "단백질": 0, "지방": 0}
    matched_foods = []

    for food in food_list:
        if food in food_db:
            info = food_db[food]
            for key in total:
                total[key] += info[key]
            matched_foods.append({**{"음식": food}, **info})
        else:
            st.warning(f"❗ '{food}'은 데이터베이스에 없어요. 다른 이름으로 입력해보세요.")

    # ✅ 결과 출력
    if matched_foods:
        st.subheader("📊 섭취한 음식과 영양 정보")
        df = pd.DataFrame(matched_foods)
        st.dataframe(df)

        st.subheader("📈 총 섭취량 vs 권장량")
        compare_df = pd.DataFrame({
            "섭취량": [total[k] for k in recommended],
            "권장량": [recommended[k] for k in recommended]
        }, index=recommended.keys())
        st.bar_chart(compare_df)

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

