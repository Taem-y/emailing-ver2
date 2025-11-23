import streamlit as st
from openai import OpenAI

# 1. 화면 기본 설정
st.set_page_config(
    page_title="프로페서 프로토콜",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 프로페서 프로토콜")
st.subheader("교수님 답장 3분 컷! AI 이메일 생성기")

# 2. API 키 설정 (안전장치 포함)
# 서버에 키가 있으면 그걸 쓰고, 없으면 입력창을 띄웁니다.
api_key = None

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.warning("⚠️ 서버에 API 키가 설정되지 않았습니다. 아래에 키를 직접 입력하세요.")
    api_key = st.text_input("OpenAI API Key", type="password")

# 3. 사용자 입력 받기
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        prof_name = st.text_input("교수님 성함", placeholder="예: 김철수 교수님")
        my_name = st.text_input("내 이름", placeholder="예: 홍길동")
    with col2:
        course_name = st.text_input("강의명", placeholder="예: 분자생물학")
        my_id = st.text_input("학번", placeholder="예: 20251234")
    
    category = st.radio("메일 목적", ["성적 이의 제기", "출석 인정 문의", "면담 요청", "과제 관련 문의"])
    reason = st.text_area("상세 내용", placeholder="상황을 구체적으로 적어주세요.")
    
    submit = st.form_submit_button("이메일 생성하기 ✨")

# 4. AI 생성 로직 (질문자님이 주신 코드 활용)
if submit:
    if not api_key:
        st.error("API 키가 없습니다. 키를 입력하거나 서버 설정을 확인하세요.")
    elif not prof_name or not reason:
        st.warning("필수 정보(교수님 성함, 상세 내용)를 입력해주세요.")
    else:
        try:
            # 클라이언트 생성
            client = OpenAI(api_key=api_key)
            
            with st.spinner("AI가 가장 정중한 표현을 고르는 중입니다..."):
                
                # --- [질문자님의 핵심 프롬프트] ---
                prompt = f"""
                당신은 예의 바르고 논리적인 대학생입니다. 아래 정보를 바탕으로 교수님께 보낼 정중한 이메일을 작성하세요.
                
                [정보]
                - 수신: {prof_name}
                - 강의: {course_name}
                - 발신: {my_name} ({my_id})
                - 목적: {category}
                - 상세 내용: {reason}
                
                [조건]
                1. 제목은 한눈에 용건을 알 수 있게 작성 (예: [문의] 과목명 - 이름)
                2. 서두에 정중한 인사와 소속 밝힘
                3. 본문은 '배움을 구하는 자세'로 정중하게 작성 (따지는 말투 금지)
                4. 마지막에 바쁘신 와중에 읽어주셔서 감사하다는 인사 포함
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                email_content = response.choices[0].message.content
                # -------------------------------

                st.success("생성 완료! 복사해서 사용하세요.")
                st.code(email_content, language="text")
                st.info("💡 Tip: 내용은 상황에 맞게 조금 수정해서 보내세요.")
                
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")


