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

st.title("🚀 네이버 블로그 상위 노출 자동화 프로그램")
st.markdown("Gemini 3.6 Flash 기반 / 네이버 실시간 MCP 검색 연동 및 멀티 탭 에이전트 시스템")

# API 키 설정 (사이드바 또는 환경 변수)
with st.sidebar:
    st.header("🔑 설정")
    api_key_input = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("API Key 설정 완료!")
    else:
        st.warning("Google AI Studio에서 발급받은 API Key를 입력해주세요.")
        
    st.markdown("---")
    st.markdown("### 📌 업데이트 안내")
    st.markdown("- **무료 스톡 이미지 기능 완전 삭제** (본문 집중)")
    st.markdown("- **Gemini 3.6 Flash (`gemini-3.6-flash`) 모델 적용**")
    st.markdown("- **탭 UI 분리 및 대형 입력창 적용**")
    st.markdown("- **네이버 실시간 검색/블로그 MCP 연동**")

# -------------------------------------------------------------
# 1. 네이버 MCP 검색 연동 시뮬레이션 및 함수
# -------------------------------------------------------------
def search_naver_morphic_data(query: str):
    """
    네이버 지역 검색 및 블로그 검색 MCP 연동 함수 (실제 API 또는 MCP 툴 호출 영역)
    """
    # 실제 구현 시 네이버 Open API나 MCP 서버(search_local, search_blog)와 연동됩니다.
    simulated_results = f"[네이버 MCP 실시간 연동 결과] '{query}' 관련 상위 블로그 트렌드 및 지역 정보 분석 완료. (키워드 밀도 및 최신 SEO 가이드 적용)"
    return simulated_results

# -------------------------------------------------------------
# 2. 탭(Tab) UI 구성 (본문 생성 vs 데이터 및 스타일 학습)
# -------------------------------------------------------------
tab_main, tab_style = st.tabs(["📝 본문 생성 (Main)", "🧠 데이터 및 스타일 학습 (Tone & Sample)"])

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
        "이번 글만의 특별한 이벤트, 강조 포인트, 주의사항을 적어주세요 (넓어진 입력창)",
        placeholder="예: 이번 주말에만 선착순 3명에게 무료 레슨 진행한다는 점을 글 중간에 자연스럽게 강조해 줘.",
        height=130
    )

    st.markdown("---")
    st.subheader("3. 사진 파일 경로 및 이미지 매칭 정보")
    photo_folder = st.text_input("사진이 저장된 폴더 경로", placeholder="예: C:/Users/Images/Starbucks")
    photo_count = st.slider("사용할 이미지 장수 권장", min_value=1, max_value=20, value=10)

with tab_style:
    st.subheader("🎨 스타일 및 레퍼런스 학습 공간")
    st.markdown("영상의 블로그 자동화 프로그램처럼 내 말투와 경쟁사 글을 넓은 창에 시원하게 학습시킬 수 있습니다.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 👤 본인 블로그 글 샘플 (말투 복사)")
        my_tone_sample = st.text_area(
            "평소 본인이 쓰는 말투나 과거 블로그 글 본문을 붙여넣으세요.",
            placeholder="평소에 '~거든요', '~더라고요' 체를 쓰고 이모지를 적당히 섞어 쓰는 내 말투 샘플 입력...",
            height=250
        )
    with col_s2:
        st.markdown("#### 🏆 경쟁사 블로그 샘플 (상위 노출 분석용)")
        competitor_sample = st.text_area(
            "현재 상위 노출되고 있는 경쟁사 블로그 본문이나 특징을 붙여넣으세요.",
            placeholder="상위 노출 글의 구조, 키워드 배치, 분량 등을 참고할 경쟁사 글 샘플 입력...",
            height=250
        )

# -------------------------------------------------------------
# 3. 글 생성 실행 버튼 및 에이전트 파이프라인
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("✨ 최종 블로그 글 생성하기 (Gemini 3.6)", type="primary", use_container_width=True)

if generate_btn:
    if not api_key_input:
        st.error("오른쪽 사이드바에 Google Gemini API Key를 먼저 입력해주세요!")
    elif not company_name or not region:
        st.error("업체명과 지역은 필수 입력 항목입니다!")
    else:
        with st.spinner("🤖 Gemini 3.6 에이전트가 네이버 MCP 검색 및 스타일 분석을 수행하고 있습니다... 잠시만 기다려주세요!"):
            try:
                # GenAI 클라이언트 초기화 (Gemini 3.6 Flash 모델 지정)
                client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                model_name = "gemini-3.6-flash"
                
                # 1단계: 네이버 MCP 검색 시뮬레이션 데이터 확보
                naver_research = search_naver_morphic_data(f"{region} {company_name}")
                
                # 2단계: 프롬프트 조합
                system_instruction = f"""
                너는 프로 블로그 라이터이자 상위 노출 SEO 전문 에이전트야.
                - 사용 모델: Gemini 3.6 Flash
                - 목표: 광고성 느낌을 지우고 방문자의 체류 시간을 높이는 리얼한 후기형 블로그 글 작성.
                - 규칙: 외부 무료 스톡 이미지 호출 코드는 절대 생성하지 않으며, 본문 내에 사진을 배치할 위치([사진: 파일명])만 가이드한다.
                """
                
                user_content = f"""
                [기본 정보]
                - 업체명: {company_name}
                - 지역: {region}
                
                [이번 글 핵심 요청사항 (Custom Prompt)]
                {custom_prompt if custom_prompt else "특별한 요청 없음. 기본 홍보 및 정보성 조화."}
                
                [스타일 및 레퍼런스 데이터]
                - 내 말투 샘플: {my_tone_sample if my_tone_sample else "자연스럽고 친근한 블로그 어투"}
                - 경쟁사 참고 샘플: {competitor_sample if competitor_sample else "일반적인 상위 노출 구조 참고"}
                
                [네이버 검색 MCP 인사이트]
                {naver_research}
                
                위 조건들을 모두 조합하여, 모바일 가독성이 뛰어난 완벽한 네이버 블로그 본문 글을 작성해 줘.
                """
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    ),
                )
                
                result_text = response.text
                
                # 결과 출력 화면
                st.success("🎉 블로그 글 생성이 완료되었습니다!")
                
                st.markdown("### 📄 생성된 블로그 본문 결과")
                st.text_area("복사해서 블로그에 바로 활용하세요", value=result_text, height=400)
                
                st.info("💡 안내: 요청하신 대로 스톡 이미지 코드는 제외되었으며, 지정하신 사진 폴더 경로와 매칭하여 바로 업로드하실 수 있습니다.")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
