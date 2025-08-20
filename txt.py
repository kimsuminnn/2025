와우! 고2 학생들이라면 한창 공부도 하고, 활동량도 많을 때잖아? 키도 쑥쑥 커야 하고, 집중력도 중요하고! 그런 너희들에게 딱 맞는, 활기찬 식단 및 영양 분석기를 만들어 줄게!

이전 버전의 코드를 **고2 학생들의 특성(성장, 활동량, 학습 등)**에 맞춰 대폭 수정할 거야.

**주요 변경 사항:**

1.  **권장 섭취량(RDA) 조정:** 고2 학생의 평균적인 성장과 활동량을 고려한 칼로리 및 영양소 권장치로 조정했어. (남학생, 여학생의 평균을 고려한 일반적인 값이며, 개인별 차이는 있을 수 있음)
2.  **식품 데이터베이스 확장:** 학생들이 즐겨 먹는 학교 급식 메뉴나 간식류(떡볶이, 라면, 김밥, 치킨 등)를 추가해서, 더 현실적인 식단 분석이 가능하도록 했어. 물론, 모든 음식은 표준적인 조리법과 1인분/100g 기준으로 설정된 거야.
3.  **맞춤형 식습관 개선 팁:** 단순히 부족/과잉을 넘어, "학습 능력", "성장", "피부 건강", "수면" 등 고등학생들이 공감할 만한 키워드와 연결하여 좀 더 공감 가는 팁을 제공하도록 했어. 다이어트 강요가 아닌 '건강하고 균형 잡힌 식습관'을 강조하는 긍정적인 메시지를 담았어.
4.  **언어 및 톤:** 앱 전체의 안내 문구나 피드백 메시지를 좀 더 친근하고 응원하는 톤으로 바꿨어.

---

**🔥 실행 방법은 이전과 동일해! 🔥**

1.  **필요 라이브러리 설치:**
    ```bash
    pip install streamlit pandas plotly fuzzywuzzy python-Levenshtein
    ```
2.  **코드 저장:** 아래 파이썬 코드를 `teen_nutrition_app.py` 같은 이름으로 저장.
3.  **앱 실행:** 터미널/명령 프롬프트에서 저장한 파일의 디렉토리로 이동하여 다음 명령어를 실행.
    ```bash
    streamlit run teen_nutrition_app.py
    ```

---

```python
# 필요한 라이브러리 불러오기
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fuzzywuzzy import process # 유사 단어 매칭을 위한 라이브러리

# --- 1. 식품 데이터베이스 (고2 학생 맞춤 확장 및 구체화) ---
# 실제 데이터는 공개된 국가 식품영양성분 데이터베이스를 참고하여 구성
# 'g' 단위는 100g 당 함량, (단위)가 붙은 음식은 해당 단위 당 함량
FOOD_DATABASE = {
    # 밥/곡물류
    "쌀밥 (1공기, 210g)": {"calories": 308, "탄수화물": 68.3, "단백질": 5.4, "지방": 0.5, "나트륨": 1, "칼륨": 60, "인": 98, "아연": 1.2, "식이섬유": 0.6},
    "현미밥 (1공기, 210g)": {"calories": 286, "탄수화물": 60.1, "단백질": 6.7, "지방": 2.4, "나트륨": 1, "칼륨": 210, "인": 280, "아연": 2.1, "식이섬유": 4.2},
    "식빵 (1장, 30g)": {"calories": 79, "탄수화물": 15.6, "단백질": 2.6, "지방": 0.9, "나트륨": 140, "철분": 0.4},
    "시리얼 (1회분, 30g)": {"calories": 110, "탄수화물": 24.5, "단백질": 2.0, "지방": 0.5, "나트륨": 180, "철분": 4.5, "엽산": 100}, # 강화 시리얼 기준

    # 국/찌개류 (주로 급식 메뉴)
    "김치찌개 (1인분, 400g)": {"calories": 185, "탄수화물": 8.8, "단백질": 12.3, "지방": 11.2, "나트륨": 1900, "칼륨": 300, "칼슘": 50, "비타민C": 5},
    "된장찌개 (1인분, 400g)": {"calories": 130, "탄수화물": 9.5, "단백질": 9.5, "지방": 6.0, "나트륨": 1700, "칼륨": 400, "칼슘": 80, "식이섬유": 4.0},
    "미역국 (1인분, 350g)": {"calories": 80, "탄수화물": 8.0, "단백질": 6.0, "지방": 2.0, "나트륨": 1200, "칼슘": 100, "요오드": 500},

    # 메인 요리/일품 요리
    "비빔밥 (1인분, 450g)": {"calories": 700, "탄수화물": 105.7, "단백질": 32.5, "지방": 15.6, "나트륨": 1100, "칼륨": 500, "철분": 3.5, "비타민A": 500, "식이섬유": 8.0},
    "불고기 (1인분, 200g)": {"calories": 500, "탄수화물": 30.0, "단백질": 28.0, "지방": 30.0, "나트륨": 800, "철분": 3.0, "아연": 3.0},
    "제육볶음 (1인분, 200g)": {"calories": 450, "탄수화물": 25.0, "단백질": 25.0, "지방": 25.0, "나트륨": 900, "철분": 2.5, "비타민B1": 0.8},
    "닭가슴살 (100g)": {"calories": 165, "탄수화물": 0, "단백질": 31, "지방": 3.6, "나트륨": 74, "칼륨": 255, "인": 200, "비타민B6": 0.6},
    "삼겹살 구이 (1인분, 200g)": {"calories": 794, "탄수화물": 0, "단백질": 35.8, "지방": 72.8, "나트륨": 100, "칼륨": 400, "철분": 1.5, "비타민B1": 0.5},
    "계란 프라이 (1개, 50g)": {"calories": 90, "탄수화물": 0.4, "단백질": 6.8, "지방": 7.0, "나트륨": 80, "비타민D": 1.0, "철분": 0.8},
    "두부 (100g)": {"calories": 76, "탄수화물": 1.9, "단백질": 8, "지방": 4.8, "칼슘": 105, "철분": 5.4, "마그네슘": 60},
    "생선구이 (고등어, 100g)": {"calories": 204, "탄수화물": 0, "단백질": 20.0, "지방": 13.0, "나트륨": 90, "비타민D": 7.0, "오메가3": 2.0},

    # 채소/과일류
    "사과 (1개, 150g)": {"calories": 78, "탄수화물": 20.1, "단백질": 0.4, "지방": 0.3, "비타민C": 7, "칼륨": 160, "식이섬유": 3.0},
    "바나나 (1개, 100g)": {"calories": 89, "탄수화물": 22.8, "단백질": 1.1, "지방": 0.3, "비타민C": 8.7, "칼륨": 358, "식이섬유": 2.6},
    "고구마 (1개, 150g)": {"calories": 130, "탄수화물": 30.0, "단백질": 2.0, "지방": 0.2, "칼륨": 470, "비타민A": 800, "비타민C": 30, "식이섬유": 4.0},
    "브로콜리 (100g)": {"calories": 34, "탄수화물": 6.6, "단백질": 2.8, "지방": 0.4, "비타민C": 89.2, "비타민K": 102, "식이섬유": 2.6},
    "샐러드 채소 (100g)": {"calories": 20, "탄수화물": 4, "단백질": 1.5, "지방": 0.2, "비타민A": 200, "비타민K": 150, "엽산": 80, "식이섬유": 2.0},
    "김치 (50g)": {"calories": 15, "탄수화물": 3.0, "단백질": 1.0, "지방": 0.2, "나트륨": 400, "비타민C": 5, "식이섬유": 1.5},

    # 유제품/음료
    "우유 (200ml)": {"calories": 103, "탄수화물": 9.4, "단백질": 6.4, "지방": 5.5, "칼슘": 240, "비타민D": 2.4, "비타민B2": 0.3},
    "오렌지주스 (200ml)": {"calories": 90, "탄수화물": 20.8, "단백질": 1.4, "지방": 0.2, "비타민C": 120, "칼륨": 400},
    "탄산음료 (350ml)": {"calories": 150, "탄수화물": 40, "단백질": 0, "지방": 0, "나트륨": 40},

    # 간식/패스트푸드
    "라면 (1봉지, 120g)": {"calories": 500, "탄수화물": 75.0, "단백질": 10.0, "지방": 18.0, "나트륨": 1900, "칼슘": 10, "철분": 0.5},
    "떡볶이 (1인분, 400g)": {"calories": 600, "탄수화물": 90.0, "단백질": 20.0, "지방": 20.0, "나트륨": 1500, "칼슘": 50},
    "김밥 (1줄, 200g)": {"calories": 300, "탄수화물": 50.0, "단백질": 12.0, "지방": 6.0, "나트륨": 600, "철분": 1.0},
    "피자 (1조각, 150g)": {"calories": 350, "탄수화물": 35.0, "단백질": 15.0, "지방": 15.0, "나트륨": 700, "칼슘": 150},
    "치킨 (순살 프라이드 100g)": {"calories": 300, "탄수화물": 10.0, "단백질": 25.0, "지방": 18.0, "나트륨": 400},
    "감자튀김 (M사이즈, 120g)": {"calories": 370, "탄수화물": 45.0, "단백질": 4.0, "지방": 20.0, "나트륨": 200},
    "초콜릿 (50g)": {"calories": 250, "탄수화물": 30.0, "단백질": 3.0, "지방": 15.0, "당류": 25.0},
    "과자 (1봉지, 60g)": {"calories": 300, "탄수화물": 35.0, "단백질": 3.0, "지방": 17.0, "나트륨": 300},
}

# --- 2. 일일 권장 섭취량 (RDA) - 고2 학생 평균 기준 근사치 ---
# 활동량 보통인 남학생과 여학생 평균을 고려한 값 (개인차 큼)
DAILY_RDA = {
    "calories": 2300,  # kcal (남학생 2500-2800, 여학생 2000-2200 고려)
    "탄수화물": 300,   # g (총 에너지의 55~65%)
    "단백질": 65,     # g (체중 kg당 1.0~1.2g, 성장기 고려)
    "지방": 65,      # g (총 에너지의 20~30%)
    "식이섬유": 25,   # g
    "비타민C": 100,   # mg
    "비타민A": 750,   # mcg
    "비타민D": 10,    # mcg (성장기 뼈 건강에 중요)
    "비타민E": 15,    # mg
    "비타민K": 75,    # mcg
    "비타민B1": 1.4,  # mg (에너지 대사에 중요)
    "비타민B2": 1.5,  # mg
    "비타민B6": 1.5,  # mg
    "비타민B12": 2.4, # mcg
    "엽산": 400,      # mcg (성장에 중요)
    "칼슘": 900,      # mg (뼈 성장 최적기)
    "철분": 14,       # mg (여학생은 더 높을 수 있음 16mg)
    "칼륨": 3500,     # mg
    "마그네슘": 350,  # mg (성장과 신경 기능)
    "인": 700,        # mg
    "아연": 12,       # mg
    "나트륨": 2000,    # mg (섭취 상한선)
    "오메가3": 1.8,  # g
    "당류": 50,       # g (WHO 권장 상한선 - 총 칼로리의 10% 미만)
}

# --- Streamlit 앱 페이지 설정 ---
st.set_page_config(layout="wide", page_title="🏃‍♀️ 고2 맞춤 식단 & 영양 분석기")

st.title("🏃‍♀️ 고2 맞춤 식단 & 영양 분석기")
st.markdown("##### 공부하느라, 활동하느라 바쁜 너희를 위한 맞춤 영양 코칭!")
st.markdown("---")

# --- 사용자 입력 섹션 ---
st.header("1. 오늘 먹은 식단을 입력해주세요")

# 선택된 음식 아이템과 섭취량을 저장할 세션 상태 초기화
if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = [] # [{'food': '쌀밥 (1공기, 210g)', 'quantity_g': 210}, ...]

col_food_input, col_quantity_input, col_add_button = st.columns([0.6, 0.2, 0.2])

with col_food_input:
    user_food_input = st.text_input(
        "음식 이름을 입력하거나 아래에서 추천되는 목록을 확인하세요!",
        placeholder="예: 쌀밥, 비빔밥, 닭가슴살, 라면, 김치찌개...",
        key="user_food_input"
    )

    recommended_food = None
    if user_food_input:
        # 유사 단어 매칭으로 추천 목록 생성
        matches = process.extractBests(user_food_input, FOOD_DATABASE.keys(), score_cutoff=60, limit=5)
        
        if matches:
            # 일치율이 높은 순서대로 드롭다운 메뉴로 제공
            selected_match = st.selectbox(
                "혹시 이 음식을 찾으시나요?",
                [f"{match[0]} (정확도 {match[1]}%)" for match in matches],
                key="match_selector"
            )
            # 실제 음식 이름만 추출 (정확도 부분 제거)
            recommended_food = selected_match.split(' (정확도')[0]
        else:
            st.warning("🤔 앗, 비슷한 음식을 찾기 어렵네요. 음식 이름을 정확하게 입력해주거나 다른 음식을 시도해보세요.")
    
with col_quantity_input:
    # 추천된 음식에 명시된 기본 그램 수를 섭취량 입력창의 기본값으로 설정
    default_g = 100.0 # 기본값은 100g
    if recommended_food and recommended_food in FOOD_DATABASE:
        import re
        # 예: "쌀밥 (1공기, 210g)" 에서 210 추출
        match = re.search(r'\(.*, (\d+\.?\d*)g\)', recommended_food) 
        if match:
            default_g = float(match.group(1))
        # 만약 '100g'으로만 명시된 음식이라면, 그대로 100g
        elif '(100g)' in recommended_food:
             default_g = 100.0


    quantity_g = st.number_input(
        f"섭취량 (그램, g)",
        min_value=1.0,
        max_value=3000.0, # 최대 3kg
        value=default_g, # 추천 음식의 기본 g 단위로 설정 시도
        step=1.0,
        key="quantity_g_input"
    )

with col_add_button:
    st.markdown("<br>" * 3, unsafe_allow_html=True) # 세로 정렬을 위한 공백
    if st.button("식단 추가!", key="add_meal_button"):
        if recommended_food and recommended_food in FOOD_DATABASE:
            st.session_state.daily_meals.append({
                "food": recommended_food,
                "quantity_g": quantity_g
            })
            st.success(f"✔️ **{recommended_food}** {quantity_g}g 추가 완료!")
            st.session_state.user_food_input = "" # 입력창 초기화
            st.experimental_rerun() # 추가 후 화면 새로고침
        else:
            st.warning("⚠️ 선택된 음식이 없거나, 아직 데이터베이스에 없는 음식이에요. 정확한 이름을 입력해주세요.")


st.markdown("---")

st.subheader("🍚 나의 오늘 식단 목록")
if not st.session_state.daily_meals:
    st.info("💡 아직 추가된 식단이 없습니다. 위에 음식과 섭취량을 입력하고 '식단 추가!' 버튼을 눌러보세요.")
else:
    meal_df = pd.DataFrame(st.session_state.daily_meals)
    # 표시용으로 'quantity_g' 컬럼명 변경
    meal_df.rename(columns={'quantity_g': '섭취량 (g)'}, inplace=True)
    meal_df.index = meal_df.index + 1 # 인덱스 1부터 시작하도록
    st.table(meal_df)

    if st.button("❌ 모든 식단 초기화 (다 지우기)", key="reset_meals_button"):
        st.session_state.daily_meals = []
        st.experimental_rerun()

st.markdown("---")

# --- 3. 영양 분석 로직 ---
total_nutrients = {nutrient: 0 for nutrient in DAILY_RDA.keys()}
# 모든 음식의 영양소 합산
for meal in st.session_state.daily_meals:
    food_name = meal['food']
    quantity_g = meal['quantity_g']
    
    if food_name in FOOD_DATABASE:
        food_info = FOOD_DATABASE[food_name]
        
        # FOOD_DATABASE에 (N공기, NNNg) 같은 형식의 기본 g을 파싱하여 비율 계산
        base_g = 100.0 # 기본 기준은 100g
        import re
        match = re.search(r'\(.*, (\d+\.?\d*)g\)', food_name)
        if match:
            base_g = float(match.group(1))
        elif '(100g)' in food_name: # 명시적으로 100g으로 기준된 경우
             base_g = 100.0


        for nutrient, value in food_info.items():
            # 칼로리 제외하고 g당 계산 (calories는 단순 합산)
            # 단, 이미 1회 제공량으로 명시된 데이터는 그 단위 그대로 사용
            if nutrient == "calories": 
                 total_nutrients["calories"] += (quantity_g / base_g) * value
            elif nutrient == "당류": # 당류는 별도 계산 (모든 음식에 당류 데이터가 있지 않을 수 있음)
                total_nutrients["당류"] += (quantity_g / base_g) * value
            else: # 나머지 영양소
                 if nutrient in total_nutrients: # total_nutrients 키에 있는 영양소만 더하기
                    total_nutrients[nutrient] += (quantity_g / base_g) * value

# --- 4. 영양 분석 결과 시각화 ---
st.header("2. ✨ 나의 영양 분석 결과")

if not st.session_state.daily_meals:
    st.warning("아직 식단을 추가하지 않았네요! 식단을 추가하면 여기에 영양 분석 결과가 나타날 거예요.")
else:
    # --- 영양소 섭취량을 권장량과 비교하는 Bullet Graph 생성 함수 ---
    def create_rda_bullet_chart(nutrient_name, intake_value, rda_value, unit=""):
        # rda_value가 0이거나 데이터에 없는 경우 안전하게 처리 (ex: 특정 영양소 없는 음식)
        if rda_value is None or rda_value == 0:
            rda_value = 1 # 0으로 나누는 것을 방지
            axis_max = 100 # 임의의 값 설정

        # 권장량 대비 200%까지 표시 (너무 과잉인 경우 그래프가 늘어나는 것 방지)
        axis_max = rda_value * 2.0
        
        # 섭취량과 권장량 비율에 따른 바(Bar) 색상 결정
        bar_color = "gray" # 기본값
        if nutrient_name == "나트륨" or nutrient_name == "당류": # 나트륨과 당류는 권장량 초과 시 주의
            if intake_value > rda_value: bar_color = "red"
            else: bar_color = "green" # 권장량 이하
        else: # 그 외 영양소는 부족/적정/과잉
            if intake_value / rda_value < 0.7: # 70% 미만: 부족
                bar_color = "orange"
            elif intake_value / rda_value > 1.3: # 130% 초과: 과잉
                bar_color = "red"
            else: # 70% ~ 130%: 적정
                bar_color = "green"

        fig = go.Figure(go.Indicator(
            mode = "number+gauge",
            value = intake_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"<span style='font-size:1.1em'>{nutrient_name} ({unit})</span><br><span style='font-size:0.8em;color:gray'>권장: {rda_value}{unit}</span>"},
            gauge = {
                'shape': "bullet",
                'axis': {'range': [0, axis_max], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': bar_color},
                'steps': [
                    {'range': [0, rda_value * 0.7], 'color': "lightgray"}, # 부족 (70% 미만)
                    {'range': [rda_value * 0.7, rda_value * 1.3], 'color': "lightblue"}, # 적정 (70% ~ 130%)
                    {'range': [rda_value * 1.3, axis_max], 'color': "lightcoral"} # 과잉 (130% 초과)
                ],
                'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': rda_value}
            }))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=50, b=10))
        return fig

    # --- 주요 영양소 (칼로리, 탄단지, 식이섬유, 나트륨, 당류) ---
    st.subheader("🔥 너의 하루 에너지는 어때?")
    main_nutrients_display = ["calories", "탄수화물", "단백질", "지방", "식이섬유", "나트륨", "당류"]
    
    main_cols = st.columns(len(main_nutrients_display))
    for i, nutrient in enumerate(main_nutrients_display):
        with main_cols[i]:
            unit = ""
            if nutrient == "calories": unit = "kcal"
            elif nutrient == "나트륨": unit = "mg"
            else: unit = "g"
            
            # 데이터가 없는 영양소는 표시하지 않음 (get으로 안전하게 접근)
            intake_val = total_nutrients.get(nutrient, 0)
            rda_val = DAILY_RDA.get(nutrient)
            
            if rda_val is not None:
                st.plotly_chart(create_rda_bullet_chart(nutrient, intake_val, rda_val, unit), use_container_width=True)
            else:
                st.markdown(f"<p style='font-size:0.8em; color:gray;'>{nutrient} (정보 없음)</p>", unsafe_allow_html=True)


    st.markdown("---")

    # --- 비타민 및 미네랄 ---
    st.subheader("💡 몸 쑥쑥, 머리 쓱쓱! 비타민 & 미네랄은?")
    micro_nutrients_display = [
        "칼슘", "철분", "비타민D", "비타민C", "비타민A", "비타민B1", "비타민B2", "비타민B6", "비타민B12", "엽산",
        "칼륨", "마그네슘", "인", "아연", "비타민E", "비타민K", "오메가3"
    ]
    
    num_cols_micros = 4 
    cols_micros = st.columns(num_cols_micros)
    
    for i, nutrient in enumerate(micro_nutrients_display):
        intake_val = total_nutrients.get(nutrient, 0)
        rda_val = DAILY_RDA.get(nutrient)
        
        if rda_val is not None:
            with cols_micros[i % num_cols_micros]:
                unit = "mg"
                if nutrient in ["비타민A", "비타민D", "비타민K", "비타민B12", "엽산"]:
                    unit = "mcg"
                elif nutrient == "오메가3":
                    unit = "g"
                
                st.plotly_chart(create_rda_bullet_chart(nutrient, intake_val, rda_val, unit), use_container_width=True)
        else:
            with cols_micros[i % num_cols_micros]:
                st.markdown(f"<p style='font-size:0.8em; color:gray;'>{nutrient} (정보 없음)</p>", unsafe_allow_html=True)


    st.markdown("---")

    # --- 5. 맞춤형 식습관 개선 팁 제공 (고2 맞춤!) ---
    st.header("3. 💖 너를 위한 맞춤형 식습관 꿀팁!")
    tips = []

    # 성장/에너지 관련 팁
    if total_nutrients["calories"] < DAILY_RDA["calories"] * 0.8:
        tips.append("**활동량과 공부량에 비해 에너지가 부족**할 수 있어요! 집중력 저하나 피로를 느낀다면, 식사량을 조금 늘리거나 견과류, 과일 같은 건강한 간식으로 에너지를 보충해 보세요.")
    elif total_nutrients["calories"] > DAILY_RDA["calories"] * 1.2:
        tips.append("오늘 칼로리를 많이 섭취했네요! 과도한 간식이나 야식을 줄이고, 균형 잡힌 식사를 유지하는 것이 좋아요. 튀긴 음식 대신 굽거나 찌는 방법을 시도해볼까요?")

    if total_nutrients["탄수화물"] < DAILY_RDA["탄수화물"] * 0.7:
        tips.append("**뇌 활동과 에너지를 위한 탄수화물**이 조금 부족할 수 있어요. 쌀밥, 현미밥, 통밀빵, 고구마 등 좋은 탄수화물을 충분히 먹어서 공부에 필요한 에너지를 채워주세요!")
    elif total_nutrients["탄수화물"] > DAILY_RDA["탄수화물"] * 1.3 and total_nutrients.get("당류",0) > DAILY_RDA["당류"] * 1.5:
        tips.append("**당류가 포함된 탄수화물 섭취가 많은 편**이에요. 라면, 떡볶이, 단 음료, 과자보다는 밥, 채소, 과일처럼 자연 상태의 탄수화물을 선택하는 게 좋아요. 피부 건강과 집중력에도 좋답니다!")
    
    if total_nutrients["단백질"] < DAILY_RDA["단백질"] * 0.8:
        tips.append("한창 성장할 시기인데 **단백질 섭취가 부족**하네요! 닭가슴살, 계란, 두부, 콩, 고기, 생선 등으로 근육을 튼튼하게 하고 면역력도 높여보세요. 키 크는 데도 도움이 될 거예요!")
    
    if total_nutrients["지방"] < DAILY_RDA["지방"] * 0.7:
        tips.append("**건강한 지방 섭취가 부족**할 수 있어요. 뇌 발달과 호르몬 균형에 필요한 좋은 지방(견과류, 등푸른 생선, 아보카도)을 잊지 말고 챙겨주세요!")
    elif total_nutrients["지방"] > DAILY_RDA["지방"] * 1.3:
        tips.append("지방을 많이 섭취했네요! 특히 튀기거나 기름진 음식을 자주 먹었다면, 굽거나 삶는 조리법으로 바꿔보는 건 어때요? 피부 트러블 관리에도 도움이 될 거예요.")

    if total_nutrients["나트륨"] > DAILY_RDA["나트륨"] * 1.2:
        tips.append("**나트륨 섭취량이 높은 편**이에요. 짠 음식은 쉽게 붓게 만들고, 장기적으로 건강에 부담을 줄 수 있어요. 국물 요리나 가공식품보다는 신선한 재료로 요리하고, 물을 충분히 마셔주는 것이 좋습니다.")

    if total_nutrients["식이섬유"] < DAILY_RDA["식이섬유"] * 0.7:
        tips.append("**식이섬유 섭취가 부족**하네요. 장 건강은 물론, 포만감을 주어 건강한 체중을 유지하는 데도 도움이 돼요! 통곡물, 채소, 과일, 해조류를 더 많이 먹어보세요.")
    
    # 뼈 건강 (고2에게 특히 중요)
    if total_nutrients.get("칼슘", 0) < DAILY_RDA["칼슘"] * 0.7 or total_nutrients.get("비타민D", 0) < DAILY_RDA["비타민D"] * 0.7:
        tips.append("**키 성장에 중요한 칼슘과 비타민D**가 부족할 수 있어요! 우유, 치즈, 뼈째 먹는 생선, 그리고 햇볕을 충분히 쬐어주는 것도 잊지 마세요.")
    
    # 철분 (여학생)
    if total_nutrients.get("철분", 0) < DAILY_RDA["철분"] * 0.7 and total_nutrients["calories"] < 2000: # 칼로리가 낮으면 철분 부족 가능성 높음
        tips.append("**철분 섭취에 신경 써주세요!** 특히 여학생이라면 더욱 중요해요. 붉은 살코기, 시금치, 콩류를 비타민C와 함께 섭취하면 흡수율이 높아진답니다.")

    # 물 섭취 권장
    tips.append("**충분한 물 섭취는 정말 중요해요!** 공부할 때나 운동할 때 늘 물병을 옆에 두고 수시로 마셔서 몸을 촉촉하게 유지해주세요.")


    if not tips:
        st.success("✨ **오늘 식단은 영양 균형이 아주아주 잘 잡혀 있습니다! 짱이에요!** 👍 지금처럼만 건강한 식습관을 유지한다면, 키도 쑥쑥! 공부도 쑥쑥! 에너지가 넘칠 거예요!")
    else:
        st.info("다음과 같은 점들을 참고해서 너의 식습관을 더욱 멋지게 만들어가는 건 어떨까요?")
        for tip in tips:
            st.markdown(f"- {tip}")

st.markdown("---")
st.markdown("""
    💡 **이 앱은 고2 학생들을 위한 영양 조언이야!**
    - 여기에 나오는 모든 영양 정보는 평균적인 고2 학생의 권장량과 일반적인 식품 데이터를 바탕으로 한 **참고 자료**야.
    - 사람마다 활동량, 건강 상태, 성장 속도가 다 다르니까, 정말 **나에게 딱 맞는 영양 상담이 필요하다면 꼭 학교 영양 선생님이나 보건 선생님, 또는 병원 영양사 선생님께 직접 물어보는 게 가장 정확해!**
""")
```
