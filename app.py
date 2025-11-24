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

# 2. API 키 설정 (안전장치)
# 서버(Secrets)에 키가 있으면 그걸 쓰고, 없으면 입력창을 띄워주는 '하이브리드' 방식
api_key = None

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.warning("⚠️ 서버에 API 키가 설정되지 않았습니다. 테스트를 위해 아래에 키를 직접 입력하세요.")
    api_key = st.text_input("OpenAI API Key", type="password")

# 3. 사용자 입력 폼 (요청하신 디자인 적용 완료)
with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        prof_name = st.text_input("교수님 성함", placeholder="예: 김철수 교수님")
        my_name = st.text_input("내 이름", placeholder="예: 홍길동")
    with col2:
        course_name = st.text_input("강의명", placeholder="예: 분자생물학")
        my_id = st.text_input("학번", placeholder="예: 20251234")
    
    category = st.radio(
        "메일을 보내는 목적:",
        ["수업 내용 질의", "성적 이의 제기 (정정 요청)", "출석 인정(결석) 문의", "면담/상담 요청", "과제 제출 지각/오류", "기타"]
    )
    
    reason = st.text_area("구체적인 사유 (AI가 참고할 내용)", placeholder="예: 기말고사 3번 문제 정답이랑 제 답안이 유사한 것 같아 확인 부탁드림")
    
    submit_btn = st.form_submit_button("이메일 생성하기 ✨")

# 4. AI 생성 로직
if submit_btn:
    # 예외 처리: 키가 없거나 필수 정보가 빠졌을 때
    if not api_key:
        st.error("API 키가 없습니다. Secrets 설정을 확인하거나 키를 입력해주세요.")
    elif not prof_name or not reason:
        st.warning("교수님 성함과 구체적인 사유는 필수 입력 사항입니다.")
    else:
        try:
            # 클라이언트 생성
            client = OpenAI(api_key=api_key)
            
            with st.spinner("AI가 가장 정중한 표현을 고르는 중입니다..."):
                
                # --- [확정된 핵심 프롬프트] ---
                prompt = f"""
                당신은 예의 바르고 논리적인 대학생입니다. 아래 정보와 예시를 바탕으로 교수님께 보낼 정중한 이메일을 작성하세요.
                [예시1]
                제목: [미생물학2] 15강 End replication problem of DNA 질문드립니다
                내용:
                안녕하세요, 미생물학2 01분반 수강중인 2024140312 생명공학부 조예은입니다.
                Eukaryote의 end replication problem of DNA와 관련하여 궁금한 점이 있어 질문 드립니다.
                lagging strand로부터 합성된 Okazaki fragment의 5' 말단 마다 RNA primer가 붙어있고, RNA primer을 제거하고 그 자리에 DNA 조각을 집어넣고 틈을 연결하기 위해서 양 끝(위,아래)에 3'-OH와 5'-P가 모두 있어야 한다고 이해했습니다. 그래서 맨 마지막에 합성된 Okazaki fragment의 경우 5' 말단의 RNA primer을 제거하고 나면 새로운 DNA가닥을 연결시킬 3'-OH가 없어서 RNA primer만 제거할 뿐 새로운 DNA 가닥을 연결할 수 없으므로 복제가 진행될 때마다 새로 합성된 DNA의 5' 말단이 짧아지게 되는게 end replication problem이라고 이해했습니다. 
                궁금한 점은 위 이유 때문에 DNA가 짧아지는게 문제라면, lagging strand 뿐만 아니라 leading strand에서도 end problem이 존재하는 것인가요? leading strand에서도 5' 말단에 RNA primer가 존재하고, 3'-OH가 없는 것은 마찬가지이니까, 똑같이 짧아지게 되는 문제가 발생하나요? ppt에는 leading strand 언급은 없이 오직 lagging strand의 Okazaki fragment만을 언급하고 있어 이 점에서 의문이 들었습니다
                감사합니다.
                
                [예시2]
                제목: [유기화학2] 9월 9일 (화) 출석 인정 요청드립니다
                내용:
                안녕하세요 이동호 교수님, 유기화학2 02분반 수강중인 2024140312 생명공학부 조예은입니다. 금일 2교시 수업의 오프라인 출석체크 과정에서 LMS 네트워크 오류가 발생하여 출석 체크를 하지 못하였습니다. 번거로우시겠지만 금일 수업 출석이 누락되지 않도록 출석 인정 처리 부탁드립니다. 
                감사합니다.

                [예시3]
                제목: [생명과학의세계] 시험 범위 문의
                내용:
                안녕하세요, 생명과학의세계 02분반을 수강 중인 생명공학부 2024140312 조예은입니다.
                기말고사 시험 범위와 관련하여 몇 가지 궁금한 점이 있어 문의드립니다.
                1.	공지사항에 따르면 시험 범위가 8주차-14주차로 안내되어 있으나, 현재 12주차 1차시(2) 강의는 동영상 없이 강의 자료만 업로드된 상황입니다. 이런 경우 강의 자료만 업로드된 주차도 시험 범위에 포함되는 것인지 궁금합니다.
                2.	13주차 역시 동영상은 없고 강의 자료만 업로드된 상태인데, 이 또한 시험 범위에 해당되는지 궁금합니다.
                3.	또한, 14주차 강의가 13주차에 업로드되면서 15주차 강의가 14주차에 업로드되었는데, 이런 경우 공지된 시험 범위인 8주차-14주차가 동영상이 실제로 업로드된 주차를 기준으로 하는지,아니면 강의 자료에 적혀 있는 주차 기준인지 궁금합니다.
                감사합니다.
                조예은 드림

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
                5. 위에 붙여준 예시를 참고하여 작성
                6. 과도한 공손함은 자제할 것
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                email_content = response.choices[0].message.content
                # -------------------------------

                st.success("생성 완료! 아래 내용을 복사해서 사용하세요.")
                st.code(email_content, language="text")
                st.info("💡 Tip: 내용은 상황에 맞게 조금 수정해서 보내세요.")
                
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")








