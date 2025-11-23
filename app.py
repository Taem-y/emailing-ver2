import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(page_title="프로페서 프로토콜", page_icon="🎓")

st.title("🎓 프로페서 프로토콜")
st.subheader("교수님 답장 3분 컷! AI 이메일 생성기")

# --- [핵심 수정 부분] ---
# Secrets에서 키를 찾아보고, 없으면 사용자에게 입력받는 "하이브리드" 방식
api_key = None

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    # Secrets가 안 먹힐 때를 대비한 비상 입력창
    st.warning("⚠️ 서버에 API 키가 설정되지 않았습니다. 임시로 아래에 키를 입력하세요.")
    api_key = st.text_input("OpenAI API Key", type="password")
# ---------------------

with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        prof_name = st.text_input("교수님 성함", placeholder="예: 김철수 교수님")
        my_name = st.text_input("내 이름", placeholder="예: 홍길동")
    with col2:
        course_name = st.text_input("강의명", placeholder="예: 분자생물학")
        my_id = st.text_input("학번", placeholder="예: 20251234")
    
    category = st.radio("목적:", ["성적 이의 제기", "출석 인정 문의", "면담 요청", "과제 관련 문의"])
    reason = st.text_area("상세 내용", placeholder="상황을 구체적으로 적어주세요.")
    
    submit_btn = st.form_submit_button("이메일 생성하기 ✨")

if submit_btn:
    if not api_key:
        st.error("API 키가 필요합니다! (Secrets 설정 또는 직접 입력)")
    elif not prof_name or not reason:
        st.warning("교수님 성함과 내용은 필수입니다.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            수신: {prof_name}, 발신: {my_name}, 강의: {course_name}, 목적: {category}
            내용: {reason}
            위 정보를 바탕으로 대학생이 교수님께 보내는 매우 정중한 이메일을 작성하세요.
            """
            
            with st.spinner("AI가 작성 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("생성 완료!")
                st.code(response.choices[0].message.content)
        except Exception as e:
            st.error(f"에러 발생: {e}")
