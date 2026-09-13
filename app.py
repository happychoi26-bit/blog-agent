import os
import time
import requests
import google.generativeai as genai
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="Pro SEO & Multi-Agent Content System",
    page_icon="👑",
    layout="wide",
)

st.title("👑 최선생의 블로그 자동화 ")
st.markdown(
    "다중 에이전트 심층 리서치 + 톤 복제 라이터 + SEO 메타 태그 최적화 엔진"
)

# --- 세션 상태 초기화 (API Key 증발 방지 포함) ---
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "article_content" not in st.session_state:
    st.session_state.article_content = None
if "raw_writer_response" not in st.session_state:
    st.session_state.raw_writer_response = None
if "research_data" not in st.session_state:
    st.session_state.research_data = None
if "competitor_analysis" not in st.session_state:
    st.session_state.competitor_analysis = None
if "style_guide" not in st.session_state:
    st.session_state.style_guide = None
if "seo_score" not in st.session_state:
    st.session_state.seo_score = 0
if "seo_grade" not in st.session_state:
    st.session_state.seo_grade = "측정 전"
if "keyword_density" not in st.session_state:
    st.session_state.keyword_density = "0%"
if "meta_description" not in st.session_state:
    st.session_state.meta_description = ""


# --- 사이드바: 입력 영역 ---
with st.sidebar:
    st.header("🔑 API 설정")
    st.session_state.user_api_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.user_api_key,
        type="password",
        placeholder="AIzaSy...",
        help="한 번 입력하면 앱을 새로고침하기 전까지 유지됩니다.",
    )

    st.header("⚙️ 콘텐츠 타겟 설정")
    company_name = st.text_input("업체명", placeholder="예: 이음뮤직학원")
    region = st.text_input(
        "지역 (랜드마크/상권 포함 추천)",
        placeholder="예: 인천논현동 (인천논현역 인근)",
    )

    content_perspective = st.selectbox(
        "📝 콘텐츠 관점 및 목적 선택",
        [
            "수강생/방문자 체험 후기형 (친근함, 솔직한 신뢰도)",
            "원장님/사업자 홍보형 (전문성, 커리큘럼, 혜택 강조)",
            "정보성 가이드형 (학원 선택 팁, 지역 정보 등 전문 리뷰)",
        ],
    )

    emoji_style_option = st.selectbox(
        "✨ 말투 & 이모지(이모티콘) 스타일 설정",
        [
            "💬 카톡 친근한 말투 + 센스 있는 텍스트 이모티콘 (ㅎㅎ, ㅠㅠ, :) 등)",
            (
                "🤍 요즘 블로그 감성 이모지 (✨, 🤍, 🫧, 💌 등 과하지 않은"
                " 포인트)"
            ),
            "🚫 이모지/이모티콘 일체 배제 (담백한 정석 텍스트)",
        ],
    )

    st.markdown("---")
    st.markdown("### ✍️ 이번 글 핵심 요청사항 (Custom Prompt)")
    custom_user_request = st.text_area(
        "이번 글에 꼭 넣고 싶은 말이나 특별히 강조할 점을 적어주세요.",
        placeholder=(
            "예: 이번 주말 무료 체험 이벤트가 있다는 걸 결론부에 꼭 강조해 줘. /"
            " 주차장이 넓다는 내용도 넣어줘."
        ),
        help="AI 라이터가 원고를 작성할 때 이 요구사항을 최우선으로 반영합니다.",
    )

    st.markdown("---")
    st.markdown("### 🖼️ 이미지 활용 옵션")
    uploaded_images = st.file_uploader(
        "직접 촬영한 사진 여러 장 업로드 (선택사항)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    image_placement_mode = st.radio(
        "이미지 배치 방식 선택",
        [
            "🤖 첨부된 사진 개수에 맞춰 본문 전체에 자동 분산 배치",
            "📍 도입부 상단에 집중 배치",
            "📍 본문 중간(핵심 시설/서비스) 집중 배치",
            "📍 결론부 직전에 집중 배치",
        ],
    )

    st.markdown("---")
    st.markdown("### 🎯 전환율 극대화 (CTA) 링크 설정")
    use_cta = st.checkbox("예약 및 문의 링크(CTA) 삽입하기", value=True)
    if use_cta:
        cta_text = st.text_input(
            "버튼/문구",
            placeholder="예: 지금 바로 무료 체험 및 상담 예약하기",
            value="👉 지금 바로 무료 체험 및 상담 예약하기",
        )
        cta_url = st.text_input(
            "연결할 링크 URL", placeholder="https://m.booking.naver.com/..."
        )
        cta_position = st.selectbox(
            "CTA 링크 배치 위치 선택",
            [
                "결론부 직전 (흥미 최고조 시점 - 추천)",
                "글 맨 하단 (마무리 단계)",
                "본문 중간 + 맨 하단 (반복 노출형)",
            ],
        )
    else:
        cta_text, cta_url, cta_position = "", "", ""

    st.markdown("---")
    st.markdown("### 🥊 경쟁사 상위 노출 블로그 분석 (선택사항)")
    competitor_text_input = st.text_area(
        "상위 노출 중인 경쟁사 블로그 본문 텍스트 복사·붙여넣기 (선택)",
        placeholder="입력하지 않아도 원고 작성이 정상적으로 가능합니다.",
    )

    st.markdown("---")
    st.markdown("### 🎨 내 말투 학습용 블로그 글 분석 (텍스트 복사)")
    my_style_text_input = st.text_area(
        "내 평소 말투가 잘 드러난 기존 블로그 글 본문 텍스트 복사·붙여넣기",
        placeholder="내가 쓴 글 중 반응이 좋았거나 평소 어투가 담긴 텍스트를 붙여넣으세요.",
    )

    st.markdown("---")
    run_button = st.button(
        "🚀 프로 에이전트 파이프라인 가동",
        type="primary",
        use_container_width=True,
    )


# --- 1. 스타일 분석가 에이전트 ---
def run_style_analyzer_agent(api_key, style_text):
    if not api_key or not style_text.strip():
        return "학습할 샘플 텍스트가 없습니다. 기본 마케팅 톤앤매너를 적용합니다."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")
        prompt = f"""
        너는 프로페셔널 문체 분석가야. 아래 사용자가 직접 작성한 실제 블로그 글 텍스트를 분석하여, 다른 AI 라이터가 이 글과 100% 똑같은 어투, 문장 끝맺음, 호흡, 스타일로 글을 쓰도록 '스타일 가이드'를 도출해 줘.
        [사용자 샘플 텍스트 데이터]
        {style_text}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"스타일 분석 중 오류 발생: {str(e)}"


# --- 2. 경쟁사 분석 에이전트 ---
def run_competitor_analyzer_agent(api_key, competitor_text):
    if not api_key or not competitor_text.strip():
        return "분석된 경쟁사 데이터가 없습니다. (선택사항 미입력)"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")
        prompt = f"""
        너는 국내 최고 수준의 SEO 마케팅 전략가야. 아래 제공된 경쟁사 블로그 본문 텍스트를 분석해 줘.
        1. 상위 노출의 핵심 원인 (어떤 키워드와 정보 구조를 썼는지)
        2. 치명적 약점 및 정보의 공백 (Gap)
        3. 우리가 검색 상위를 뺏어오기 위해 본문에 반드시 담아야 할 차별화 포인트
        [경쟁사 블로그 본문 데이터]
        {competitor_text}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"경쟁사 분석 중 오류 발생: {str(e)}"


# --- 3. 심층 리서처 에이전트 ---
def run_researcher_agent(api_key, company_name, region, perspective):
    if not api_key:
        return {"trends": "⚠️ API Key가 입력되지 않았습니다.", "keywords": []}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")
        prompt = f"""
        지역 '{region}'에 위치한 업체 '{company_name}'와 관련하여, 선택된 관점('{perspective}')에 맞추어 최신 트렌드 및 소비자들이 궁금해하는 핵심 소주제들을 정리해 줘.
        """
        response = model.generate_content(prompt)
        return {
            "trends": response.text,
            "keywords": [
                f"{region} {company_name}",
                f"{region} 추천",
                "솔직 후기",
                "전문",
            ],
        }
    except Exception as e:
        return {"trends": f"리서치 중 오류 발생: {str(e)}", "keywords": []}


# --- 4. 톤 복제 라이터 에이전트 ---
def run_writer_agent(
    api_key,
    company_name,
    region,
    perspective,
    style_guide,
    competitor_analysis,
    research_trends,
    image_count,
    placement_mode,
    use_cta,
    cta_text,
    cta_url,
    cta_position,
    custom_request,
    emoji_style,
):
    if not api_key:
        return "⚠️ API Key가 입력되지 않았습니다."

    image_instruction = f"""
    [이미지 및 시각 자료 배치 가이드]
    - 사용자가 직접 업로드한 사진: {image_count}장
    - 배치 방식: [{placement_mode}]
    - 원고 내에서 사진이 필요한 위치마다 적절한 마크(`[📸 이미지 삽입 위치 - 추천 설명: ...]`)를 위 규칙에 맞추어 자연스럽게 삽입해 주세요.
    """

    cta_instruction = ""
    if use_cta:
        cta_instruction = f"""
        [행동 유도(CTA) 링크 삽입 가이드]
        - 삽입 위치: [{cta_position}]
        - 버튼 문구/텍스트: "{cta_text}"
        - 연결 링크 URL: "{cta_url}"
        - 위 지정된 위치에 독자가 클릭하기 쉽도록 마크다운 링크 형태(예: `[{cta_text}]({cta_url})`)로 자연스럽게 배치해 주세요.
        """

    custom_instruction = ""
    if custom_request.strip():
        custom_instruction = f"""
        [🚨 작성자 특별 커스텀 요청사항 (최우선 반영 필수)]
        - 작성자가 이번 글에 특별히 강조하거나 포함해달라고 요청한 내용입니다:
        "{custom_request}"
        - 위 요청사항이 본문 내용 속에 어색하지 않고 자연스럽게 녹아들도록 반드시 포함하여 작성해 주세요.
        """

    emoji_rule = f"""
    [말투 & 이모지 스타일 지침: {emoji_style}]
    - 만약 '카톡 친근한 말투 + 센스 있는 텍스트 이모티콘' 선택시: 카톡에서 대화하듯 편안하고 친근한 어조와 함께 'ㅎㅎ', 'ㅠㅠ', ':) 같은 자연스러운 텍스트 이모티콘을 적재적소에 센스 있게 섞어서 작성.
    - 만약 '요즘 블로그 감성 이모지' 선택시: 촌스러운 옛날 이모지가 아니라, 요즘 감성 블로그에서 트렌디하게 쓰는 '✨', '🤍', '🫧', '💌' 같은 미니멀하고 세련된 이모지만 은은하게 포인트로 사용.
    - 만약 '이모지/이모티콘 일체 배제' 선택시: 기호나 이모지 없이 오롯이 깔끔한 텍스트 문장만으로 전개.
    """

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")

        prompt = f"""
        너는 상위 노출을 지배하는 수석 블로그 라이터 에이전트이자 최고급 타이틀 전략가야.
        
        [가장 중요한 작성 원칙: 문체 100% 동기화]
        아래 '작성자 스타일 가이드'의 어투, 문장 끝맺음, 호흡을 철저하게 준수하여 글을 써라.
        
        {emoji_rule}

        [👑 상위 노출 전문 타이틀 전략 엔진 규칙]
        반드시 본문 작성 전, 맨 상단에 **서로 다른 마케팅 전략을 가진 상위 노출 최적화 제목 후보 3가지**를 아래 포맷으로 명확히 도출해 줘:
        1. **[타입 A - SEO 검색 유입 극대화형]**: 핵심 지역/업종 키워드를 맨앞에 배치한 제목
        2. **[타입 B - CTR(클릭률) 폭발형 / 공감·후기형]**: 독자의 호기심과 감정을 자극하는 제목
        3. **[타입 C - 신뢰도 및 전환 유도형]**: 전문가 권위와 베네핏을 주는 제목
        - *각 제목 아래에 "이 제목을 추천하는 마케팅 전략적 이유"를 1~2줄씩 덧붙일 것.*

        {image_instruction}
        {cta_instruction}
        {custom_instruction}

        [경쟁사 분석 리포트 반영 (선택사항)]
        {competitor_analysis}

        [작성자 스타일 가이드]
        {style_guide}

        [심층 리서치 참고자료]
        {research_trends}

        [작업 지시 사항]
        - 업체명: {company_name}
        - 지역: {region}
        - 콘텐츠 관점/목적: {perspective}
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 원고 작성 중 오류 발생: {str(e)}"


# --- 5. 고도화된 SEO 분석 및 메타 태그 엔진 ---
def analyze_seo_performance(article_text, company_name, region):
    score = 65
    company_count = article_text.count(company_name) if company_name else 0
    region_core = region.split()[0] if region else ""
    region_count = article_text.count(region_core) if region_core else 0

    if company_count > 0:
        score += 10
    if region_count > 0:
        score += 10

    total_words = len(article_text.split())
    keyword_total_hits = company_count + region_count
    density_val = (
        (keyword_total_hits / total_words) * 100 if total_words > 0 else 0
    )

    if 1.0 <= density_val <= 3.5:
        score += 10
    elif density_val > 5.0:
        score -= 15

    if article_text.count("##") >= 3:
        score += 5
    if 700 <= len(article_text) <= 2000:
        score += 5

    score = max(45, min(score, 95))
    if score >= 88:
        grade = "A+등급 (상위 노출 최적화 우수)"
    elif score >= 78:
        grade = "A등급 (양호함)"
    elif score >= 65:
        grade = "B등급 (보통 - 내용 보완 권장)"
    else:
        grade = "C등급 (검색 최적화 미흡)"

    clean_meta = (
        article_text.replace("#", "")
        .replace("*", "")
        .replace("\n", " ")[:150]
        .strip()
    )

    return score, grade, f"{round(density_val, 1)}%", clean_meta


# --- 파이프라인 실행 버튼 ---
if run_button:
    if not st.session_state.user_api_key:
        st.warning("⚠️ 사이드바에 Gemini API Key를 먼저 입력해주세요!")
    elif not company_name or not region:
        st.warning("⚠️ 업체명과 지역은 필수 입력 항목입니다.")
    else:
        img_count = len(uploaded_images) if uploaded_images else 0
        with st.status(
            "🚀 멀티 에이전트 파이프라인 가동 중...", expanded=True
        ) as status:
            st.write("🎨 [1/5] 스타일 분석 에이전트: 말투 텍스트 분석 중...")
            st.session_state.style_guide = run_style_analyzer_agent(
                st.session_state.user_api_key, my_style_text_input
            )
            st.success("✔ 스타일 분석 완료")

            st.write("🥊 [2/5] 경쟁사 분석 에이전트: 텍스트 심층 분석 중...")
            st.session_state.competitor_analysis = (
                run_competitor_analyzer_agent(
                    st.session_state.user_api_key, competitor_text_input
                )
            )
            st.success("✔ 경쟁사 심층 분석 완료")

            st.write("🔍 [3/5] 리서처 에이전트: 트렌드 및 키워드 분석 중...")
            st.session_state.research_data = run_researcher_agent(
                st.session_state.user_api_key,
                company_name,
                region,
                content_perspective,
            )
            st.success("✔ 리서처 완료")

            st.write(
                "✍️ [4/5] 톤 복제 라이터 에이전트: 커스텀 요청 반영 원고 작성"
                " 중..."
            )
            raw_res = run_writer_agent(
                api_key=st.session_state.user_api_key,
                company_name=company_name,
                region=region,
                perspective=content_perspective,
                style_guide=st.session_state.style_guide,
                competitor_analysis=st.session_state.competitor_analysis,
                research_trends=st.session_state.research_data["trends"],
                image_count=img_count,
                placement_mode=image_placement_mode,
                use_cta=use_cta,
                cta_text=cta_text,
                cta_url=cta_url,
                cta_position=cta_position,
                custom_request=custom_user_request,
                emoji_style=emoji_style_option,
            )
            st.session_state.raw_writer_response = raw_res
            st.session_state.article_content = raw_res
            st.success("✔ 라이터 완료")

            st.write(
                "🧩 [5/5] 어셈블러 에이전트: SEO 지표 평가 및 메타 태그 생성 중..."
            )
            score, grade, density, meta_desc = analyze_seo_performance(
                st.session_state.article_content, company_name, region
            )
            st.session_state.seo_score = score
            st.session_state.seo_grade = grade
            st.session_state.keyword_density = density
            st.session_state.meta_description = meta_desc

            status.update(
                label="🎉 상위 노출 맞춤형 콘텐츠 패키지가 완성되었습니다!",
                state="complete",
                expanded=False,
            )

        st.balloons()


# --- 결과 대시보드 출력 ---
if st.session_state.article_content is not None:
    st.markdown("---")
    st.subheader("📊 프로 파이프라인 결과 대시보드")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📝 전략적 타이틀 & 톤 복제 원고",
            "🥊 경쟁사 심층 분석 리포트",
            "🎨 학습된 스타일 가이드",
            "📈 SEO & 리서치 분석",
        ]
    )

    with tab1:
        st.markdown("### 📝 상위 노출 맞춤형 타이틀 후보군 및 본문 원고")
        st.info(
            "✨ 아래에서 마음에 드는 **최종 제목**을 선택하시면, 다운로드 시 해당"
            " 제목이 맨 위에 쏙 장착됩니다!"
        )

        selected_title_choice = st.radio(
            "✨ [선택] 블로그에 최종 적용할 대표 타이틀 고르기",
            [
                "타입 A (SEO 검색 유입 극대화형) 제목 사용",
                "타입 B (CTR 클릭률 폭발형 / 공감·후기형) 제목 사용",
                "타입 C (신뢰도 및 전환 유도형) 제목 사용",
                "제목 후보 전체 포함해서 다운로드",
            ],
            horizontal=True,
        )

        # 업로드된 이미지 미리보기
        if uploaded_images:
            st.success(
                f"🖼️ **직접 업로드한 총 {len(uploaded_images)}장의 사진이"
                f" [{image_placement_mode}] 규칙에 맞춰 연동되었습니다.**"
            )
            img_cols = st.columns(min(len(uploaded_images), 4))
            for idx, img_file in enumerate(uploaded_images):
                with img_cols[idx % 4]:
                    st.image(
                        img_file,
                        caption=f"첨부 이미지 #{idx+1}",
                        use_container_width=True,
                    )

        with st.container(border=True):
            st.markdown(st.session_state.article_content)

        clean_download_content = st.session_state.article_content
        if "타입 A" in selected_title_choice:
            clean_download_content = (
                "# [타입 A 적용 타이틀]\n" + st.session_state.article_content
            )
        elif "타입 B" in selected_title_choice:
            clean_download_content = (
                "# [타입 B 적용 타이틀]\n" + st.session_state.article_content
            )
        elif "타입 C" in selected_title_choice:
            clean_download_content = (
                "# [타입 C 적용 타이틀]\n" + st.session_state.article_content
            )

        st.download_button(
            label="📥 선택한 타이틀이 적용된 마크다운 원고 다운로드",
            data=clean_download_content,
            file_name=f"{company_name or 'blog'}_content.md",
            mime="text/markdown",
        )

    with tab2:
        st.markdown("### 🥊 경쟁사 상위 노출 글 심층 분석 및 킬러 전략")
        with st.container(border=True):
            st.markdown(st.session_state.competitor_analysis)

    with tab3:
        st.markdown("### 🎨 AI가 분석한 나의 블로그 말투/문체 페르소나")
        with st.container(border=True):
            st.markdown(st.session_state.style_guide)

    with tab4:
        st.markdown("### 📈 검색엔진 최적화(SEO) 및 메타 태그 진단")
        col1, col2, col3 = st.columns(3)
        col1.metric("현실적 SEO 점수", f"{st.session_state.seo_score}점")
        col2.metric("키워드 밀도", st.session_state.keyword_density)
        col3.metric("검색 포털 경쟁력", st.session_state.seo_grade)

        st.markdown("---")
        st.markdown("#### 🏷️ 검색 포털 노출용 메타 설명 (Meta Description)")
        st.info(
            "네이버 및 구글 검색 결과에 snippet(요약문)으로 노출되는 추천"
            f" 텍스트입니다:\n\n`{st.session_state.meta_description}...`"
        )

        st.markdown("---")
        st.markdown("#### 🔍 리서처 에이전트 분석 결과")
        st.markdown(st.session_state.research_data["trends"])

        st.markdown("#### 🔑 추출된 핵심 키워드")
        for kw in st.session_state.research_data["keywords"]:
            st.markdown(f"- `{kw}`")

else:
    st.info(
        "👈 사이드바에서 **업체명, 지역, 커스텀 요청사항, 말투/이모지 스타일**"
        " 등을 입력한 뒤 **[프로 에이전트 파이프라인 가동]** 버튼을 눌러보세요."
    )
