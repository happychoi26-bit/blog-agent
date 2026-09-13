import os
import requests
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
st.markdown("Gemini 3.6 Flash 기반 / 멀티 에이전트 / 다중 사진 매칭 및 SEO 분석 탭 분리")

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("🔑 API 설정")
    api_key_input = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("Gemini API Key 설정 완료!")
    else:
        st.warning("Google AI Studio API Key를 입력해주세요.")
        
    st.markdown("---")
    st.markdown("### 🔍 네이버 검색 API (선택 사항)")
    naver_client_id = st.text_input("Naver Client ID", type="password")
    naver_client_secret = st.text_input("Naver Client Secret", type="password")

# -------------------------------------------------------------
# 1. 네이버 블로그 검색 API 연동 모듈
# -------------------------------------------------------------
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = ""
if "seo_report" not in st.session_state:
    st.session_state["seo_report"] = ""

def search_naver_blog_real(query: str, client_id: str, client_secret: str):
    if not client_id or not client_secret:
        return "[알림] 네이버 API 키 미입력 상태: Gemini 3.6 모델의 자체 지식 기반 리서치로 대체합니다."
    
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {"query": query, "display": 5, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if not items:
                return f"'{query}'에 대한 검색 결과가 없습니다."
            result_summary = f"[네이버 실시간 검색 API 연동 성공] '{query}' 상위 블로그 요약:\n"
            for i, item in enumerate(items, 1):
                clean_title = item['title'].replace('<b>', '').replace('</b>', '')
                clean_desc = item['description'].replace('<b>', '').replace('</b>', '')
                result_summary += f"{i}. 제목: {clean_title} / 내용: {clean_desc[:100]}...\n"
            return result_summary
        else:
            return f"[네이버 API 오류] 코드: {response.status_code}"
    except Exception as e:
        return f"[네이버 API 통신 에러] {str(e)}"

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
        placeholder="예: 이번 주말에만 선착순 3명에게 무료 레슨 진행한다는 점을 강조해 줘.",
        height=130
    )

    st.markdown("---")
    st.subheader("3. 사진 파일 다중 업로드 및 매칭")
    uploaded_files = st.file_uploader(
        "사진 파일 다중 선택 (여러 장 업로드 가능)", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
    )
    
    uploaded_file_names = []
    if uploaded_files:
        uploaded_file_names = [file.name for file in uploaded_files]
        with st.expander("업로드된 사진 파일명 확인하기"):
            for name in uploaded_file_names:
                st.write(f"- 📁 {name}")

with tab_style:
    st.subheader("🎨 스타일 및 레퍼런스 학습 공간")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 👤 본인 블로그 글 샘플 (말투 복사)")
        my_tone_sample = st.text_area("평소 본인이 쓰는 말투나 과거 블로그 글 본문을 붙여넣으세요.", height=280)
    with col_s2:
        st.markdown("#### 🏆 경쟁사 블로그 샘플 (상위 노출 분석용)")
        competitor_sample = st.text_area("현재 상위 노출되고 있는 경쟁사 블로그 본문이나 특징을 붙여넣으세요.", height=280)

with tab_seo:
    st.subheader("📊 SEO 분석 및 에이전트 리포트")
    # 세션에 저장된 SEO 리포트 출력 (탭 이동해도 유지됨)
    if st.session_state["seo_report"]:
        st.markdown(st.session_state["seo_report"])
    else:
        st.info("💡 아직 생성된 리포트가 없습니다. '본문 생성' 탭에서 글을 생성해주세요!")

# -------------------------------------------------------------
# 3. 멀티 에이전트 실행 파이프라인 (본문/SEO 분리 생성으로 안정성 강화)
# -------------------------------------------------------------
st.markdown("---")
generate_btn = st.button("✨ 멀티 에이전트 가동 및 블로그 글 생성하기", type="primary", use_container_width=True)

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
            
            progress_text.text("🔍 [1단계] 리서치 및 상위 노출 트렌드 분석 중...")
            naver_research = search_naver_blog_real(f"{region} {company_name}", naver_client_id, naver_client_secret)
            
            photo_context = "업로드된 사진 없음"
            if uploaded_file_names:
                photo_context = "사용자가 업로드한 실제 사진 파일명 리스트:\n" + "\n".join([f"- {name}" for name in uploaded_file_names])
            
            # 공통 배경 데이터 묶음
            base_context = f"""
            [기본 정보] - 업체명: {company_name} / 지역: {region}
            [핵심 요청사항] {custom_prompt if custom_prompt else "일반적인 정보성 후기"}
            [사진 매칭 데이터] {photo_context}
            [말투 및 레퍼런스] 본인 말투: {my_tone_sample or "친근한 어투"} / 경쟁사: {competitor_sample or "일반 구조"}
            [리서치 데이터] {naver_research}
            """

            # [단계 2] 블로그 본문 생성
            progress_text.text("✍️ [2단계] 라이터 에이전트가 최적화 블로그 본문을 작성 중입니다...")
            body_prompt = f"{base_context}\n\n위 데이터를 바탕으로 네이버 상위 노출에 최적화된 리얼 후기 블로그 본문만 작성해 줘. 사진이 들어갈 자리에 [사진: 파일명] 가이드를 포함해 줘."
            body_response = client.models.generate_content(model=model_name, contents=body_prompt)
            st.session_state["generated_content"] = body_response.text

            # [단계 3] SEO 분석 리포트 별도 생성 (파싱 오류 원천 차단)
            progress_text.text("📊 [3단계] SEO 분석 에이전트가 상위 노출 점수와 피드백을 채점 중입니다...")
            seo_prompt = f"다음은 방금 작성된 블로그 본문입니다:\n\n{body_response.text}\n\n이 글을 바탕으로 네이버 SEO 상위 노출 관점에서 100점 만점 점수, 키워드 배치 상태, 그리고 개선 피드백을 마크다운 리포트로 상세히 작성해 줘."
            seo_response = client.models.generate_content(model=model_name, contents=seo_prompt)
            st.session_state["seo_report"] = seo_response.text
            
            progress_text.empty()
            st.success("🎉 블로그 본문 생성 및 SEO 분석 리포트 작성이 완료되었습니다! [SEO 분석 및 리포트] 탭을 확인해보세요.")
            
        except Exception as e:
            progress_text.empty()
            st.error(f"오류가 발생했습니다: {e}")

# 본문 탭 하단에 최종 생성된 본문 표시
if st.session_state["generated_content"]:
    st.markdown("---")
    st.subheader("📄 최종 생성된 블로그 본문")
    st.text_area("블로그에 복사해서 붙여넣으세요", value=st.session_state["generated_content"], height=450)
