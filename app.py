import streamlit as st
from openai import OpenAI

# 1. 화면 기본 설정
st.set_page_config(
    page_title="교수님께 이메일 써줘!!",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 교수님께 이메일 써줘!!")
st.subheader("많은 실제 이메일 사례를 기반으로 한 이메일 작성 AI")

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
        my_division = st.text_input("학과/학부", placeholder="예: 생명공학부")
        my_id = st.text_input("학번", placeholder="예: 20251234")
    
    category = st.radio(
        "메일을 보내는 목적:",
        ["수업 내용 질의", "성적 이의 제기(정정 요청)", "출석 인정 문의", "과제 제출 지각/오류", "기타"]
    )
    
    reason = st.text_area("구체적인 사유 (AI가 참고할 내용을 편하게 쓰면 됨!)", placeholder="예: LMS 오류로 과제가 제출되지 않았는데 이메일로 제출해도 괜찮을지")
    
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

                [예시1]
                제목: [미생물학2] 15강 End replication problem of DNA 질문드립니다
                내용:
                안녕하세요, 미생물학2 01분반 수강중인 2024140312 생명공학부 조예은입니다. 
                Eukaryote의 end replication problem of DNA와 관련하여 궁금한 점이 있어 질문 드립니다. 
                lagging strand로부터 합성된 Okazaki fragment의 5' 말단 마다 RNA primer가 붙어있고, RNA primer을 제거하고 그 자리에 DNA 조각을 집어넣고 틈을 연결하기 위해서 양 끝(위,아래)에 3'-OH와 5'-P가 모두 있어야 한다고 이해했습니다. 그래서 맨 마지막에 합성된 Okazaki fragment의 경우 5' 말단의 RNA primer을 제거하고 나면 새로운 DNA가닥을 연결시킬 3'-OH가 없어서 RNA primer만 제거할 뿐 새로운 DNA 가닥을 연결할 수 없으므로 복제가 진행될 때마다 새로 합성된 DNA의 5' 말단이 짧아지게 되는게 end replication problem이라고 이해했습니다. 궁금한 점은 위 이유 때문에 DNA가 짧아지는게 문제라면, lagging strand 뿐만 아니라 leading strand에서도 end problem이 존재하는 것인가요? leading strand에서도 5' 말단에 RNA primer가 존재하고, 3'-OH가 없는 것은 마찬가지이니까, 똑같이 짧아지게 되는 문제가 발생하나요? ppt에는 leading strand 언급은 없이 오직 lagging strand의 Okazaki fragment만을 언급하고 있어 이 점에서 의문이 들었습니다. 
                감사합니다.

                [예시2]
                제목: [유기화학2] 9월 9일 (화) 출석 인정 요청드립니다
                내용:
                안녕하세요 이동호 교수님, 유기화학2 02분반 수강중인 2024140312 생명공학부 조예은입니다. 
                금일 2교시 수업의 오프라인 출석체크 과정에서 LMS 네트워크 오류가 발생하여 출석 체크를 하지 못하였습니다. 번거로우시겠지만 금일 수업 출석이 누락되지 않도록 출석 인정 처리 부탁드립니다. 
                감사합니다.

                [예시3]
                제목: [식물의학개론] 시험지 확인 일정 관련 문의 드립니다.
                내용:
                정의환 교수님께,
                안녕하세요, 저는 식물의학개론을 수강한 생명공학부 2024140253 박현영 입니다. 다름이 아니라 LMS에 공지하신 화요일 시간대는 제가 개인 사정으로 불가능하여 혹시 가능하신 다른 날이 있는지 양해를 구하고자 메일 드립니다. 저는 수요일 모든 시간대, 목요일 오후 5시 이전, 금요일 오후 1시 이후 모두 가능합니다. 번거롭게 해드려 죄송하며, 가능한 시간을 회신 주시면 그 시간에 맞춰 방문하겠습니다. 답변 기다리겠습니다. 감사합니다.
                박현영드림

                [예시4]
                제목: 생명공학에서 바라본 인체의 신비 출석에 관한 건(2024140301 양형석)
                내용:
                안녕하세요
                생명공학에서 바라본 인체의 신비 수업을 수강한 2024140301 양형석입니다.
                출석과 관련하여 4/10(목), 5/8(목)에 병원을 방문한 이후 KUPID 상으로 진단서 및 진료확인서를 제출하였으나 반영되지 않은 것으로 보여서 이메일로 문의드립니다.
                관련하여 4/10(목), 5/8(목) 진단서 및 진료확인서를 첨부하였으니 확인해주시고 반영해주시면 감사하겠습니다.
                양형석 드림.

                [정보]
                - 수신: {prof_name}
                - 강의: {course_name}
                - 발신: {my_name} ({my_division} , {my_id})
                - 목적: {category}
                - 상세 내용: {reason}

                [가장 중요한 조건]
                1. 입력하지 않은 정보 및 정확하지 않은 정보에 대하여 추측하여 쓰지 말 것
                2. 상대가 교수이므로 기본적으로 공손함과 예의를 갖출 것
                
                [조건]
                1. 제목은 한눈에 용건을 알 수 있게 작성
                2. 서두에 정중한 인사와 소속 밝힘(발신에 대한 정보를 모두 밝힐 것)
                3. 과도한 공손과 예의는 자제할 것(극존칭을 사용하지 않을 것)
                4. 마지막에 바쁘신 와중에 읽어주셔서 감사하다는 인사 포함
                5. 분량이 너무 짧지않도록 적절히 작성할 것
                6. 예시 내용을 참고하여 작성할 것

        


                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                email_content = response.choices[0].message.content
                st.success("생성 완료! 아래 내용을 복사해서 사용하세요.")
                st.code(email_content, language="text")
                st.info("💡 Tip: 내용은 상황에 맞게 조금 수정해서 보내세요.")
           
                
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")



































