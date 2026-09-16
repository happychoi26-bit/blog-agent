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

st.markdown("Gemini 3.6 Flash 기반 / 모바일 자동 줄바꿈(엔터) 최적화 및 100% 긍정 톤 모듈")



# API 키 설정 (사이드바)

with st.sidebar:

    st.header("🔑 API 설정")

    api_key_input = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

    if api_key_input:

        os.environ["GEMINI_API_KEY"] = api_key_input

        st.success("Google Gemini API Key 설정 완료!")

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

    "🧠 레퍼런스 및 SEO 설정", 

    "📊 SEO 분석 및 리포트"

])



with tab_main:

    st.subheader("1. 기본 정보 및 타겟 키워드 설정")

    col1, col2 = st.columns(2)

    with col1:

        company_name = st.text_input("업체명 (상호명)", placeholder="예: 이음뮤직학원")

    with col2:

        target_keyword = st.text_input("메인 타겟 키워드", placeholder="예: 인천논현동실용음악학원")



    st.markdown("---")

    st.subheader("2. 콘텐츠 목적 및 작성 관점 선택")

    writing_mode = st.radio(

        "작성할 글의 성격과 시점을 선택하세요",

        [

            "📝 후기형 (수강생 / 고객 입장에서 직접 체험하고 쓰는 리얼 후기)", 

            "📚 정보성 (학원 / 업체 입장에서 전문 지식을 전달하는 가이드 글)", 

            "🎬 쇼츠 스크립트 (학원 / 업체 입장에서 1분 이내로 눈길을 사로잡는 숏폼 영상 대본)"

        ],

        index=0

    )



    st.markdown("---")

    st.subheader("3. 키워드 배치 전략 (SEO 최적화)")

    keyword_strategy = st.selectbox(

        "타겟 키워드를 본문에 녹여낼 배치 방식을 선택하세요",

        [

            "💡 [추천] 스마트 균등 분산 (제목, 서두, 본문 중간, 결론에 자연스럽게 배치)",

            "🚀 상단 집중형 (검색 유입 극대화를 위해 글의 시작 부분에 키워드 강한 배치)",

            "🔀 자연스러운 랜덤 녹임 (인위적이지 않게 문장 흐름에 맞춰 툭툭 던지듯 분산)"

        ]

    )



    st.markdown("---")

    st.subheader("4. 핵심 요청사항 (Custom Prompt)")

    custom_prompt = st.text_area(

        "이번 글만의 특별한 이야기, 강조하고 싶은 시설이나 특징을 적어주세요",

        placeholder="예: 월간 공연 프로그램과 수강생 합주실 환경을 강조해 줘.",

        height=120

    )



with tab_style:

    st.subheader("🎨 레퍼런스 및 경쟁사 분석 공간")

    st.markdown("#### 🏆 경쟁사 블로그 샘플 (상위 노출 분석용)")

    competitor_sample = st.text_area(

        "현재 상위 노출되고 있는 경쟁사 블로그 본문이나 벤치마킹하고 싶은 문장 구조를 붙여넣으세요.", 

        height=320,

        placeholder="경쟁사 글의 핵심 키워드 배치나 서두 구조를 입력하면 에이전트가 완벽히 분석하여 반영합니다."

    )



with tab_seo:

    st.subheader("📊 SEO 분석 및 에이전트 리포트")

    if st.session_state["seo_report"]:

        st.markdown(st.session_state["seo_report"])

    else:

        st.info("💡 아직 생성된 리포트가 없습니다. '본문 생성' 탭에서 글을 생성해주세요!")



# -------------------------------------------------------------

# 3. 멀티 에이전트 실행 파이프라인 (Gemini 3.6 Flash 활용)

# -------------------------------------------------------------

st.markdown("---")

generate_btn = st.button("✨ 멀티 에이전트 가동 및 콘텐츠 생성하기", type="primary", use_container_width=True)



if generate_btn:

    if not api_key_input:

        st.error("오른쪽 사이드바에 Google Gemini API Key를 먼저 입력해주세요!")

    elif not company_name or not target_keyword:

        st.error("업체명과 메인 타겟 키워드는 필수 입력 항목입니다!")

    else:

        progress_text = st.empty()

        

        try:

            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

            model_name = "gemini-3.6-flash"

            

            progress_text.text("🔍 [1단계] 실시간 리서치 및 타겟 키워드 트렌드 분석 중...")

            naver_research = search_naver_blog_real(target_keyword, naver_client_id, naver_client_secret)

            

            # [모바일 엔터 최적화 및 100% 긍정 톤 가이드라인]

            tone_guideline = """

            [작성 절대 원칙 (매우 중요 - 모바일 가독성 및 톤 규격)]

            1. 모바일 줄바꿈(엔터) 포맷 적용: 

               - 긴 문단을 절대 쓰지 말고, 스마트폰 화면 기준으로 눈이 편안하도록 한 줄 또는 두 줄마다 엔터(줄바꿈)를 쳐서 호흡을 짧게 끊어주세요.

               - 예시 형식:

                 찾으시는 분들을 위해

                 음악을 더 재미있고 풍성하게 즐길 수 있는

                 특별한 이야기들을 전해드리려고 해요

            2. 100% 긍정 마인드셋 유지: 

               - 독자의 불안감을 유발하거나 아쉬움을 지적하는 부정적 표현(예: 혼자 하면 지친다, 어렵다 등)은 일체 배제합니다.

               - 모든 내용을 "혼자서도 즐겁지만 함께하면 배로 즐겁고 행복하다"는 식의 밝고 긍정적인 희망 에너지만 담아내세요.

            3. 상업적 강요 및 특수문자 배제: 

               - '당장 연락 주세요', '문의가 쇄도합니다' 같은 억지 홍보 멘트를 빼고, 마크다운 별표 기호(**) 남발 없이 담백하게 작성하세요.

            """



            if "후기형" in writing_mode:

                mode_instruction = f"{tone_guideline}\n[작성 모드: 후기형 (수강생/고객 입장)] - 실제 수강생의 시점에서 즐거웠던 체험 경험을 모바일 친화적인 호흡으로 진솔하게 작성."

            elif "정보성" in writing_mode:

                mode_instruction = f"{tone_guideline}\n[작성 모드: 정보성 (학원/업체 입장)] - 전문가의 따뜻한 시각에서 유익한 정보를 모바일 가독성에 맞춰 친절하게 안내하듯 작성."

            else:

                mode_instruction = f"{tone_guideline}\n[작성 모드: 쇼츠 스크립트 (학원/업체 입장)] - 1분 안에 시청자의 미소를 자아낼 수 있도록 [화면 연출]과 [나레이션 대사]로 나누어 모바일 가독성 있게 작성."



            # 공통 배경 데이터 묶음

            base_context = f"""

            [기본 정보] - 업체명: {company_name} / 메인 타겟 키워드: "{target_keyword}"

            {mode_instruction}

            [키워드 배치 전략] {keyword_strategy} (이 스타일에 맞춰 타겟 키워드가 문맥 속에 자연스럽고 부드럽게 녹아들도록 할 것)

            [핵심 요청사항] {custom_prompt if custom_prompt else "일반적인 정보성 내용"}

            [경쟁사 레퍼런스 참고] {competitor_sample or "일반 상위 노출 구조"}

            [네이버 검색 리서치 데이터] {naver_research}

            """



            # [단계 2] 콘텐츠 본문 생성

            progress_text.text("✍️ [2단계] 라이터 에이전트가 모바일 엔터 형식 및 100% 긍정 톤으로 콘텐츠를 작성 중입니다...")

            body_prompt = f"{base_context}\n\n위 데이터를 바탕으로 네이버 상위 노출에 최적화된 고품질 결과물을 작성해 줘. 타겟 키워드('{target_keyword}')가 어색하지 않게 잘 녹아들어야 한다."

            body_response = client.models.generate_content(model=model_name, contents=body_prompt)

            st.session_state["generated_content"] = body_response.text



            # [단계 3] SEO 분석 리포트 별도 생성

            progress_text.text("📊 [3단계] SEO 분석 에이전트가 키워드 배치 상태와 상위 노출 점수를 채점 중입니다...")

            seo_prompt = f"다음은 방금 작성된 콘텐츠입니다:\n\n{body_response.text}\n\n이 글을 바탕으로 메인 타겟 키워드('{target_keyword}')가 네이버 SEO 관점에서 적재적소에 잘 배치되었는지 평가하고, 100점 만점 점수와 개선 피드백을 마크다운 리포트로 상세히 작성해 줘."

            seo_response = client.models.generate_content(model=model_name, contents=seo_prompt)

            st.session_state["seo_report"] = seo_response.text

            

            progress_text.empty()

            st.success("🎉 콘텐츠 생성 및 SEO 분석 리포트 작성이 완료되었습니다! [SEO 분석 및 리포트] 탭을 확인해보세요.")

            

        except Exception as e:

            progress_text.empty()

            st.error(f"오류가 발생했습니다: {e}")



# 본문 탭 하단에 최종 생성된 콘텐츠 표시

if st.session_state["generated_content"]:

    st.markdown("---")

    st.subheader("📄 최종 생성된 콘텐츠 결과물")

    st.text_area("블로그에 복사해서 사용하세요", value=st.session_state["generated_content"], height=480)
