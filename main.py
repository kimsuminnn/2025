import streamlit as st

# 페이지 설정
st.set_page_config(page_title="MBTI Career Finder", page_icon="💼", layout="wide")

# 스타일 (배경 그라데이션 + 글자 예쁘게)
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom right, #ffecd2, #fcb69f);
    }
    .job-card {
        padding: 15px;
        border-radius: 12px;
        background-color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .mbti-title {
        font-size: 28px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# MBTI별 직업 데이터
mbti_jobs = {
    "INTJ": ["📊 데이터 사이언티스트", "🧠 전략 기획가", "🏛 정책 분석가"],
    "ENTP": ["🚀 기업가", "📢 마케팅 디렉터", "🎨 창작자"],
    "INFJ": ["💬 심리상담사", "✍️ 작가", "🎓 교육 전문가"],
    "ESFP": ["🎭 배우", "🎉 이벤트 플래너", "📺 광고 크리에이터"],
}

mbti_description = {
    "INTJ": "🦉 **전략적**이고 **분석적인** 성향으로 장기 계획 수립에 강점이 있습니다.",
    "ENTP": "💡 **창의적**이고 **새로운 아이디어**를 시도하는 것을 즐깁니다.",
    "INFJ": "🌱 **깊이 있는 통찰력**과 **공감 능력**을 바탕으로 사람들을 돕습니다.",
    "ESFP": "☀️ **에너지 넘치고 사교적**인 성격으로 현장에서 활약합니다.",
}

# 제목
st.title("💼✨ MBTI 기반 화려한 직업 추천")
st.markdown("당신의 **MBTI**를 선택하면 ✨반짝이는✨ 직업 추천을 받으실 수 있어요! 💖")

# MBTI 선택
selected_mbti = st.selectbox("🔍 MBTI를 선택하세요:", list(mbti_jobs.keys()))

# 추천 결과
if selected_mbti:
    st.markdown(f"<div class='mbti-title'>🔮 {selected_mbti} 유형의 추천 직업</div>", unsafe_allow_html=True)
    
    for job in mbti_jobs[selected_mbti]:
        st.markdown(f"<div class='job-card'>{job}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(mbti_description[selected_mbti])

# 푸터
st.markdown("🌟 만든이: **MBTI Career Finder** | 🖤 즐거운 진로 탐험 되세요!")
