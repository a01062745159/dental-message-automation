import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

st.set_page_config(page_title="서울수려한치과", layout="wide")
st.title("🏥 서울수려한치과 - 자동 문자 발송")

@st.cache_resource
def get_gsheet():
    try:
        scope = ['https://spreadsheets.google.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gsheet_creds"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key(st.secrets["spreadsheet_id"])
    except Exception as e:
        st.error(f"연동 오류: {e}")
        return None

templates = {
    '전화상담+예약': '안녕하세요 {환자명}님! 저는 {담당자명}입니다.\n\n감사합니다. {예약일}에 예약해주신 내용 정리해드립니다.\n\n{개인정보}에 대해 잘 기억하고 있습니다.\n\n{걱정부분}에 대해서는 {해결책}으로 도움이 될 것 같습니다.\n\n{진료내용_링크}\n\n병원 위치: {병원위치}\n예약 변경: 010-6584-2874\n\n{예약일}에 뵙겠습니다!\n\n홈페이지: https://www.suryeohan.com/',
    '전화상담+미예약': '안녕하세요 {환자명}님! 저는 {담당자명}입니다.\n\n감사합니다.\n\n{의구심부분}에 대해 고민이 많으신 것 같습니다.\n{공감_신뢰감}\n\n{해결책}으로 도움이 될 것입니다.\n\n{진료내용_링크}\n\n이번 기회에 치료를 받으시길 권유합니다!\n\n예약: http://map.naver.com/p/entry/place/21697698\n문의: 010-6584-2874',
    '내원상담+예약': '안녕하세요 {환자명}님! 저는 {담당자명}입니다.\n\n오늘 내원해주셔서 감사합니다!\n\n{치료결정_감사}\n\n진행 계획:\n{치료계획}\n\n{진료내용_링크}\n\n신경 쓸 점: {특별주의사항}\n\n예약 변경: 010-6584-2874\n\n{예약일}에 뵙겠습니다!',
    '내원상담+미예약': '안녕하세요 {환자명}님! 저는 {담당자명}입니다.\n\n오늘 내원해주셔서 감사합니다.\n\n{의구심부분}이 걱정되시는군요.\n\n{구체적해결책}으로 해결 가능합니다.\n\n{공감_사례}하셨습니다.\n\n{진료내용_링크}\n\n예약: http://map.naver.com/p/entry/place/21697698\n문의: 010-6584-2874',
    '리콜종료': '안녕하세요 {환자명}님! 저는 {담당자명}입니다.\n\n지속적인 연락으로 불편을 드렸다면 사과드립니다.\n더 이상 연락드리지 않을 예정입니다.\n\n{치료미실행_아쉬움}\n\n{합병증경고}이 발생할 수 있습니다.\n\n치료가 필요하시면 언제든지 010-6584-2874로 연락주세요!'
}

fields = {
    '전화상담+예약': ['환자명', '예약일', '개인정보', '진료내용_링크', '걱정부분', '해결책', '병원위치', '담당자명'],
    '전화상담+미예약': ['환자명', '의구심부분', '공감_신뢰감', '해결책', '진료내용_링크', '담당자명'],
    '내원상담+예약': ['환자명', '예약일', '치료결정_감사', '치료계획', '진료내용_링크', '특별주의사항', '담당자명'],
    '내원상담+미예약': ['환자명', '의구심부분', '구체적해결책', '공감_사례', '진료내용_링크', '담당자명'],
    '리콜종료': ['환자명', '치료미실행_아쉬움', '합병증경고', '담당자명']
}

tab1, tab2, tab3 = st.tabs(["📱 기록 입력", "✉️ 메시지 생성", "📊 발송 관리"])

with tab1:
    st.subheader("📱 통화 기록 입력")
    situation = st.selectbox("상황 선택", list(fields.keys()))
    input_data = {}
    cols = st.columns(2)
    for idx, field in enumerate(fields[situation]):
        with cols[idx % 2]:
            input_data[field] = st.text_area(field, height=80, key=f"input_{field}")
    
    if st.button("💾 저장"):
        try:
            ss = get_gsheet()
            if ss:
                sheet_name = f"기록_{situation}"
                try:
                    ws = ss.worksheet(sheet_name)
                except:
                    ws = ss.add_worksheet(title=sheet_name, rows=100, cols=10)
                row = [datetime.now().strftime("%Y-%m-%d %H:%M"), situation] + [input_data.get(f, '') for f in fields[situation]]
                ws.append_row(row)
                st.success(f"✅ {input_data.get('환자명', '저장')} 완료!")
        except Exception as e:
            st.error(f"❌ 오류: {e}")

with tab2:
    st.subheader("✉️ 메시지 생성")
    try:
        ss = get_gsheet()
        if ss:
            all_records = []
            for sheet in ss.worksheets():
                if sheet.title.startswith('기록_'):
                    for record in sheet.get_all_values()[1:]:
                        if record and len(record) > 2:
                            all_records.append({'시간': record[0], '상황': record[1], '환자명': record[2]})
            if all_records:
                idx = st.selectbox("기록 선택", range(len(all_records)), format_func=lambda i: f"{all_records[i]['환자명']} - {all_records[i]['상황']}")
                record = all_records[idx]
                if st.button("✉️ 메시지 생성"):
                    template = templates[record['상황']]
                    for field in fields[record['상황']]:
                        template = template.replace(f"{{{field}}}", f"[{field}]")
                    st.session_state.msg = template
                if 'msg' in st.session_state:
                    msg_text = st.text_area("메시지", st.session_state.msg, height=300)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 복사"):
                            st.code(msg_text)
                    with col2:
                        if st.button("✅ 발송완료"):
                            st.success(f"✅ {record['환자명']} 발송 완료!")
            else:
                st.info("기록이 없습니다.")
    except Exception as e:
        st.error(f"❌ 오류: {e}")

with tab3:
    st.subheader("📊 발송 관리")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ 완료", "5")
    col2.metric("⏳ 대기", "2")
    col3.metric("📅 이번주", "7")
