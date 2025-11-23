import streamlit as st
from openai import OpenAI

# 1. 화면 설정
st.set_page_config(page_title="프로페서 프로토콜", page_icon="🎓")

st.title("🎓 프로페서 프로토콜")
st.subheader("교수님 답장 3분 컷! AI 이메일 생성기")

# 2. API 키 처리 (여기가 핵심! 안 죽는 코드)
api_key = None

# (1) 서버에 비밀번호(Secrets)가 설정되어 있으면 그걸 씀
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
# (2) 없으면 사용자에게 직접 입력받음 (에러 방지용)
else:
    st.warning("⚠️ 아직 서버에 API 키가 없습니다. (테스트용으로 직접 입력하세요)")
    api_key = st.text_input("OpenAI API Key 입력", type="password")

# 3. 입력 폼
with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        prof_name = st.text_input("교수님 성함", placeholder="예: 김철수 교수님")
        my_name = st.text_input("내 이름", placeholder="예: 홍길동")
    with col2:
        course_name = st.text_input("강의명", placeholder="예: 분자생물학")
        my_id = st.text_input("학번", placeholder="예: 20251234")
    
    category = st.radio("목적", ["성적 이의 제기", "출석 인정 문의", "면담 요청", "과제 관련 문의"])
    reason = st.text_area("상세 내용", placeholder="구체적인 사유를 적어주세요.")
    
    submit = st.form_submit_button("이메일 생성하기 ✨")

# 4. AI 작동
if submit:
    if not api_key:
        st.error("API 키가 필요합니다!")
    elif not prof_name or not reason:
        st.warning("정보를 입력해주세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"수신:{prof_name}, 발신:{my_name}, 강의:{course_name}, 목적:{category}, 내용:{reason}. 대학생이 교수님께 보내는 정중한 메일을 써줘."
            
            with st.spinner("AI가 작성 중..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("완료!")
                st.code(response.choices[0].message.content)
        except Exception as e:
            st.error(f"에러 발생: {e}")