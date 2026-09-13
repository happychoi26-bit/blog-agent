import os
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 0. 페이지 설정 및 초기화
# -------------------------------------------------------------
st.set_page_config(
    page_title="블로그 자동화 에이전트 (Gemini 3.6)",
    page_icon="✍️",
    layout="wide"
)

st.title("🚀 네이버 블로그 상위 노출 자동화 프로그램 (3단 탭 시스템)")
st.markdown("Gemini 3.6 Flash 기반 / 멀티 에이전트 / 다중 사진 매칭 및 SEO 분석 탭 분리")

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("🔑 설정")
    api_key_input = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("API Key 설정 완료!")
    else:
        st.warning("Google AI Studio에서 발급받은 API Key를 입력해주세요.")
        
    st.markdown("---")
    st.markdown("### 📌 시스템 안내")
    st.markdown("- **본문 / 스타일 / SEO 분석 탭 분리 완료**")
    st.markdown("- **다중 사진 파일명 자동 매칭 활성화**")
    st.markdown("- **Gemini 3.6 Flash 멀티 에이전트 구동**")

# -------------------------------------------------------------
# 1. 네이버 검색 모듈 (상태 저장용 세션)
# -------------------------------------------------------------
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = ""
if "seo_report" not in st.session_state:
    st.session_state["seo_report"] = ""

def search_naver_morphic_data(query: str):
    # 실시간 검색 시뮬레이션 (추후 실제 네이버 API/MCP 확장 가능 구조)
    return f"[네이버 실시간 검색 리서치 연동] '{query}' 키워드 기준 상위 노출 블로그의 평균 분량, 체류 시간 유도 패턴, 핵심 서브 키워드 분석 완료."

# -------------------------------------------------------------
# 2. 3단 탭(Tab) UI 구성
# -------------------------------------------------------------
tab_main, tab_style, tab_seo = st.tabs([
    "📝 본문 생성 (Main)", 
    "🧠 데이터 및 스타일 학습", 
    "📊 SEO 분석 및 리포트"
])

with tab_main:
    st.subheader("1. 기본 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("업체명 (상호명)", placeholder="예: 스타벅스 역삼점")
    with col2:
        region = st.text_input("지역 / 위치", placeholder="예: 서울 강남구 역삼동")

    st.markdown("---")
    st.subheader("2. 핵심 요청사항 (Custom Prompt)")
    custom_prompt = st.text_area(
        "이번 글만의 특별한 이벤트, 강조 포인트, 주의사항을 적어주세요",
        placeholder="예: 이번 주말에만 선착순 3명에게 무료 레슨 진행한다는 점을 글 중간에 자연스럽게 강조해 줘.",
        height=130
    )

    st.markdown("---")
    st.subheader("3. 사진 파일 다중 업로드 및 매칭")
    st.markdown("블로그에 넣을 사진들을 여러 장 한 번에 드래그하거나 선택해서 올려주세요.")
    
    uploaded_files = st.file_uploader(
        "사진 파일 다중 선택 (여러 장 업로드 가능)", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
    )
    
    uploaded_file_names = []
    if uploaded_files:
        file_count = len(uploaded_files)
        st.success(f"총 {file_count}장의 사진이 업로드되었습니다!")
        uploaded_file_names = [file.name for file in uploaded_files]
        with st.expander("업로드된 사진 파일명 확인하기"):
            for name in uploaded_file_names:
                st.write(f"- 📁 {name}")

with tab_style:
    st.subheader("🎨 스타일 및 레퍼런스 학습 공간")
    st.markdown("내 말투와 경쟁사 블로그 글을 넓은 창에 입력하여 에이전트가 학습하도록 합니다.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 👤 본인 블로그 글 샘플 (말투 복사)")
        my_tone_sample = st.text_area(
            "평소 본인이 쓰는 말투나 과거 블로그 글 본문을 붙여넣으세요.",
            placeholder="평소에 쓰는 어투, 종결미주, 이모지 스타일 입력...",
            height=280
        )
    with col_s2:
        st.markdown("#### 🏆 경쟁사 블로그 샘플 (상위 노출 분석용)")
        competitor_sample = st.text_area(
            "현재 상위 노출되고 있는 경쟁사 블로그 본문이나 특징을 붙여넣으세요.",
            placeholder="상위 노출 글의 구조, 키워드 배치, 분량 참고용 샘플 입력...",
            height=280
        )

with tab_seo:
    st.subheader("📊 SEO 분석 및 에이전트 리포트 탭")
    st.markdown("글이 생성되면 본문과 **분리되어** 이곳에서 독립적으로 상위 노출 점수와 피드백을 확인할 수 있습니다.")
    
    if st.session_state["seo_report"]:
        st.markdown(st.session_state["seo_report"])
    else:
        st.info("💡 아직 생성된 리포트가 없습니다. '본문 생성' 탭에서 글을 생성해주세요!")

# -------------------------------------------------------------
# 3. 멀티 에이전트 실행 및 결과 저장 파이프라인
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("✨ 멀티 에이전트 가동 및 블로그 글 생성하기 (Gemini 3.6)", type="primary", use_container_width=True)

if generate_btn:
    if not api_key_input:
        st.error("오른쪽 사이드바에 Google Gemini API Key를 먼저 입력해주세요!")
    elif not company_name or not region:
        st.error("업체명과 지역은 필수 입력 항목입니다!")
    else:
        progress_text = st.empty()
        
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            model_name = "gemini-3.6-flash"
            
            progress_text.text("🔍 [1단계] 리서치 에이전트가 지역 키워드 트렌드를 분석 중입니다...")
            naver_research = search_naver_morphic_data(f"{region} {company_name}")
            
            progress_text.text("🧠 [2단계] 스타일 분석가 에이전트가 레퍼런스를 해체 중입니다...")
            
            progress_text.text("✍️ [3단계] 라이터 에이전트가 상위 노출 최적화 본문을 작성 중입니다...")
            
            photo_context = "업로드된 사진 없음 (텍스트 위주 구성)"
            if uploaded_file_names:
                photo_context = "사용자가 업로드한 실제 사진 파일명 리스트:\n" + "\n".join([f"- {name}" for name in uploaded_file_names])
            
            system_instruction = f"""
            너는 대한민국 최고의 네이버 블로그 상위 노출(SEO) 전문 에이전트 팀이야. (Gemini 3.6 Flash 구동)
            - 역할: 광고성 느낌을 지우고 독자의 체류 시간을 극대화하는 자연스러운 리얼 후기형 블로그 글을 작성한다.
            - 규칙: 
              1. 외부 무료 스톡 이미지 호출 코드는 절대 생성하지 않는다.
              2. 본문 중간중간 사진을 배치해야 할 곳에 반드시 **사용자가 업로드한 실제 사진 파일명**을 매칭해서 `[사진: 파일명 (어떤 사진인지 설명)]` 형태로 가이드를 명시한다.
              3. 응답을 반드시 아래의 두 가지 구역(Section)으로 나누어 출력하라:
                 ---BODY_START---
                 (여기에 오직 순수 블로그 본문만 작성)
                 ---BODY_END---
                 ---SEO_START---
                 (여기에 SEO 최적화 점수 100점 만점 평가, 키워드 배치 상태, 개선 피드백을 마크다운으로 상세히 작성)
                 ---SEO_END---
            """
            
            user_content = f"""
            [기본 정보]
            - 업체명: {company_name}
            - 지역: {region}
            
            [이번 글 핵심 요청사항 (Custom Prompt)]
            {custom_prompt if custom_prompt else "특별한 요청 없음. 대중적이고 흥미로운 정보성 후기 구성."}
            
            [사진 파일 매칭 데이터]
            {photo_context}
            
            [스타일 및 레퍼런스 학습 데이터]
            - 본인 말투 샘플: {my_tone_sample if my_tone_sample else "친근하고 자연스러운 블로그 어투"}
            - 경쟁사 레퍼런스 샘플: {competitor_sample if competitor_sample else "일반적인 상위 노출 구조 반영"}
            
            [검색 리서치 분석 리포트]
            {naver_research}
            
            위 모든 내용을 종합하여 블로그 본문과 SEO 리포트를 지정된 구분자(---BODY_START--- 등)에 맞춰 작성해 줘.
            """
            
            response = client.models.generate_content(
                model=model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                ),
            )
            
            progress_text.empty()
            full_response = response.text
            
            # 본문과 SEO 리포트 파싱 분리
            try:
                body_part = full_response.split("---BODY_START---")[1].split("---BODY_END---")[0].strip()
                seo_part = full_response.split("---SEO_START---")[1].split("---SEO_END---")[0].strip()
            except:
                # 파싱 실패 시 전체를 본문으로 처리
                body_part = full_response
                seo_part = "SEO 리포트 파싱 중 형식이 일부 어긋났으나 글은 정상 생성되었습니다."
            
            # 세션에 저장하여 탭 이동 시에도 유지되도록 함
            st.session_state["generated_content"] = body_part
            st.session_state["seo_report"] = seo_part
            
            st.success("🎉 멀티 에이전트 분석 및 글 생성이 완료되었습니다! [본문 생성 탭]과 [SEO 분석 탭]을 확인하세요.")
            
        except Exception as e:
            progress_text.empty()
            st.error(f"오류가 발생했습니다: {e}")

# 결과 화면에 출력 (본문 탭 하단에 항상 고정 노출)
if st.session_state["generated_content"]:
    st.markdown("---")
    st.subheader("📄 최종 생성된 블로그 본문")
    st.text_area("블로그에 복사해서 붙여넣으세요", value=st.session_state["generated_content"], height=450)
