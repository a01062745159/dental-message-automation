import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울수려한치과 - 자동 문자 발송", layout="wide", initial_sidebar_state="expanded")

# CSS 스타일
st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: bold; color: #1f77b4; }
    .section-title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 20px; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }
    .error-box { background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

# Google Sheets 연동
@st.cache_resource
def get_gsheet():
    try:
        scope = ['https://spreadsheets.google.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gsheet_creds"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(st.secrets["spreadsheet_id"])
        return spreadsheet
    except Exception as e:
        st.error(f"Google Sheets 연동 오류: {str(e)}")
        return None

# 템플릿 정의
TEMPLATES = {
    '전화상담+예약': """안녕하세요 {환자명}님! 저는 서울수려한치과의 {담당자명}입니다.

전화 상담해주셔서 정말 감사합니다. {예약일}에 예약해주신 내용 정리해드립니다.

전화 중에 알려주신 {개인정보}에 대해 잘 기억하고 있습니다.

{걱정부분}에 대해서는 {해결책}으로 도움이 될 거라 생각합니다.

{진료내용_링크}

병원 오시는 방법: {병원위치}
예약 변경이 필요하시면 010-6584-2874로 연락주세요.

{예약일}에 직접 뵙고 인사드리겠습니다!

더 알아보기:
홈페이지 https://www.suryeohan.com/
네이버 플레이스 http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome""",

    '전화상담+미예약': """안녕하세요 {환자명}님! 저는 서울수려한치과의 {담당자명}입니다.

전화 상담해주셔서 정말 감사합니다.

{의구심부분}에 대해 고민이 많으신 것 같은데, 제 개인적인 경험을 나누고 싶습니다. {공감_신뢰감}

이렇게 하면 {해결책}할 수 있습니다.

{진료내용_링크}

이번 기회에 건강한 치아로 되돌아가시길 진심으로 권유합니다!

바로 예약하기: http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome

더 궁금한 점이 있으시면 010-6584-2874로 편하게 연락주세요!""",

    '내원상담+예약': """안녕하세요 {환자명}님! 저는 서울수려한치과의 {담당자명}입니다.

오늘 내원해주셔서 진심으로 감사합니다!

{치료결정_감사} 다음과 같이 진행될 예정입니다:
{치료계획}

{진료내용_링크}

진료 시 특별히 신경쓸 점: {특별주의사항}

예약 변경이 필요하시면 010-6584-2874로 언제든지 연락주세요.

{예약일}에 다시 뵙겠습니다!

더 보기: 네이버 리뷰 http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome""",

    '내원상담+미예약': """안녕하세요 {환자명}님! 저는 서울수려한치과의 {담당자명}입니다.

오늘 내원해주셨는데 예약을 하지 않으신 부분이 이해가 됩니다.

{의구심부분}이(가) 걱정되시는 것 같습니다. 이 부분은 {구체적해결책}으로 충분히 해결 가능합니다.

실제로 많은 환자분들이 {공감_사례}하시고 만족해하셨습니다.

{진료내용_링크}

예약하기: http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome

더 궁금한 사항은 010-6584-2874로 편하게 연락주세요!""",

    '리콜종료': """안녕하세요 {환자명}님! 저는 서울수려한치과의 {담당자명}입니다.

지속적인 연락으로 불편을 드렸다면 진심으로 사과드립니다. 더이상 연락드리지 않을 예정입니다.

다만 {치료미실행_아쉬움}한 부분이 있습니다.

치료를 미루게 되면 {합병증경고}이 발생할 수 있습니다.

건강한 치아는 저희 치과가 아니어도 꼭 치료를 받으셔야 합니다.

앞으로 치료가 필요하실 때는 언제든지 010-6584-2874로 연락주세요!

예약하기: http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome"""
}

# 필드 정의 (상황별)
FIELD_MAPPING = {
    '전화상담+예약': ['환자명', '예약일', '개인정보', '진료내용_링크', '걱정부분', '해결책', '병원위치', '담당자명'],
    '전화상담+미예약': ['환자명', '의구심부분', '공감_신뢰감', '해결책', '진료내용_링크', '담당자명'],
    '내원상담+예약': ['환자명', '예약일', '치료결정_감사', '치료계획', '진료내용_링크', '특별주의사항', '담당자명'],
    '내원상담+미예약': ['환자명', '의구심부분', '구체적해결책', '공감_사례', '진료내용_링크', '담당자명'],
    '리콜종료': ['환자명', '치료미실행_아쉬움', '합병증경고', '담당자명']
}

# 메인 UI
st.markdown('<p class="main-title">🏥 서울수려한치과 - 자동 문자 발송 시스템</p>', unsafe_allow_html=True)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📱 통화 기록 입력", "✉️ 문자 생성", "📊 발송 관리"])

# ======================== TAB 1: 통화 기록 입력 ========================
with tab1:
    st.markdown('<p class="section-title">📱 통화 기록 입력</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        situation = st.selectbox(
            "상황을 선택하세요",
            options=['전화상담+예약', '전화상담+미예약', '내원상담+예약', '내원상담+미예약', '리콜종료'],
            key='situation_select'
        )
    
    with col2:
        st.write("")  # 간격
    
    # 동적 입력 필드
    st.markdown('<p class="section-title">📝 정보 입력</p>', unsafe_allow_html=True)
    
    input_data = {}
    fields = FIELD_MAPPING.get(situation, [])
    
    # 2열 레이아웃
    cols = st.columns(2)
    for idx, field in enumerate(fields):
        col = cols[idx % 2]
        with col:
            input_data[field] = st.text_area(
                label=field,
                height=80,
                key=f"input_{field}"
            )
    
    # 저장 버튼
    if st.button("💾 저장", key="save_btn", use_container_width=True):
        try:
            spreadsheet = get_gsheet()
            if spreadsheet:
                # 해당 시트 선택
                sheet_name = f"기록_{situation}"
                try:
                    ws = spreadsheet.worksheet(sheet_name)
                except:
                    # 시트 없으면 생성
                    ws = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)
                
                # 데이터 저장
                row = [datetime.now().strftime("%Y-%m-%d %H:%M"), situation]
                for field in fields:
                    row.append(input_data.get(field, ''))
                
                ws.append_row(row)
                
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ 저장 완료!</strong><br>
                    환자: {input_data.get('환자명', '미입력')}<br>
                    상황: {situation}
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <strong>❌ 저장 실패</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)

# ======================== TAB 2: 문자 생성 ========================
with tab2:
    st.markdown('<p class="section-title">✉️ 문자 생성 (담당자용)</p>', unsafe_allow_html=True)
    
    # 미처리 기록 조회
    st.markdown('<p class="section-title">📋 미처리 기록</p>', unsafe_allow_html=True)
    
    try:
        spreadsheet = get_gsheet()
        if spreadsheet:
            # 모든 기록 시트 조회
            all_records = []
            for sheet in spreadsheet.worksheets():
                if sheet.title.startswith('기록_'):
                    records = sheet.get_all_values()
                    for record in records[1:]:  # 헤더 제외
                        if record and len(record) > 2:
                            all_records.append({
                                '시간': record[0],
                                '상황': record[1],
                                '환자명': record[2] if len(record) > 2 else '미입력'
                            })
            
            if all_records:
                # 데이터프레임으로 표시
                df = pd.DataFrame(all_records)
                
                # 선택 가능하게
                selected_idx = st.selectbox(
                    "기록 선택",
                    range(len(all_records)),
                    format_func=lambda i: f"{all_records[i]['환자명']} ({all_records[i]['상황']}) - {all_records[i]['시간']}"
                )
                
                selected_record = all_records[selected_idx]
                
                # 메시지 생성
                if st.button("✉️ 메시지 생성", use_container_width=True):
                    situation = selected_record['상황']
                    template = TEMPLATES.get(situation, '')
                    
                    # 실제 데이터로 템플릿 채우기
                    message = template
                    for field in FIELD_MAPPING.get(situation, []):
                        # 여기서는 시뮬레이션 (실제로는 저장된 데이터 사용)
                        message = message.replace(f"{{{field}}}", f"[{field}]")
                    
                    st.session_state.generated_message = message
                    st.success("✅ 메시지 생성 완료!")
                
                # 생성된 메시지 표시
                if 'generated_message' in st.session_state:
                    st.markdown('<p class="section-title">📄 생성된 메시지</p>', unsafe_allow_html=True)
                    
                    message_box = st.text_area(
                        "메시지 내용",
                        value=st.session_state.generated_message,
                        height=300,
                        disabled=False
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📋 복사하기", use_container_width=True):
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>✅ 메시지가 준비되었습니다!</strong><br>
                                아래 텍스트를 복사하여 카톡/문자로 발송하세요.
                            </div>
                            """, unsafe_allow_html=True)
                            st.code(message_box)
                    
                    with col2:
                        if st.button("✅ 발송완료", use_container_width=True):
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>✅ 발송 완료되었습니다!</strong><br>
                                환자: {selected_record['환자명']}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("📭 아직 기록이 없습니다. 통화 기록을 입력해주세요.")
    except Exception as e:
        st.error(f"데이터 조회 오류: {str(e)}")

# ======================== TAB 3: 발송 관리 ========================
with tab3:
    st.markdown('<p class="section-title">📊 발송 관리</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ 발송완료", "5건")
    with col2:
        st.metric("⏳ 미발송", "2건")
    with col3:
        st.metric("📅 이번주", "7건")
    
    st.markdown('<p class="section-title">📋 상세 기록</p>', unsafe_allow_html=True)
    
    # 샘플 데이터
    sample_data = {
        '환자명': ['송호선', '김영희', '박민준'],
        '상황': ['전화상담+예약', '전화상담+미예약', '내원상담+예약'],
        '발송상태': ['✅ 발송완료', '⏳ 미발송', '✅ 발송완료'],
        '발송일시': ['2024-05-15 14:30', '2024-05-16 10:15', '2024-05-17 16:45']
    }
    
    df_sample = pd.DataFrame(sample_data)
    st.dataframe(df_sample, use_container_width=True)

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>📞 병원: 010-6584-2874 | 🌐 홈페이지: https://www.suryeohan.com/<br>
    📍 네이버: http://map.naver.com/p/entry/place/21697698?placePath=%2Fhome</p>
</div>
""", unsafe_allow_html=True)
