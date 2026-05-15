import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import pandas as pd
import base64

# 페이지 설정
st.set_page_config(page_title="서울수려한치과 - 자동 문자 발송", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: bold; color: #1f77b4; }
    .section-title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 20px; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 5px; }
    .error-box { background-color: #f8d7da; padding: 15px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_gsheet():
    try:
        # secrets에서 JSON 문자열 가져오기
        creds_json = st.secrets["gsheet_creds"]
        
        # 문자열인 경우 JSON으로 파싱
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            creds_dict = dict(creds_json)
        
        scope = [
            'https://spreadsheets.google.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(st.secrets["spreadsheet_id"])
        return spreadsheet
    except Exception as e:
        st.error(f"❌ Google Sheets 연동 오류: {str(e)}")
        return None

# 템플릿
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

    '전화상담+미예약': """안녕하세요 {환자명}
