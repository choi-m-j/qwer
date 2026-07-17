import streamlit as st
import pandas as pd
import altair as alt

# 1. 화면 기본 설정 (넓은 화면 사용)
st.set_page_config(page_title="선생님의 안전 나침반", layout="wide")
st.title("🧭 선생님의 안전 나침반")
st.subheader("데이터 융합을 통한 다방향 학교 안전사고 예측 대시보드")

# [추가] 게시판 데이터를 임시 저장할 세션 상태 초기화 (프로토타입용)
if 'board_data' not in st.session_state:
    st.session_state.board_data = []

# 2. 통합 데이터 불러오기 (zip 파일 기준)
@st.cache_data
def load_data():
    return pd.read_csv('total_accident_data.zip', compression='zip')

df = load_data()

# 3. 왼쪽 사이드바 (조건 입력 및 게시판 폼)
st.sidebar.header("상황을 선택해주세요 👇")
school_level = st.sidebar.selectbox("학교급", df['학교급'].unique())
time_category = st.sidebar.selectbox("사고시간", df['사고시간'].unique())
location = st.sidebar.selectbox("사고장소", df['사고장소'].unique())

st.sidebar.markdown("---")

# [추가] 위험 시설물 신고 폼 (사이드바 하단)
st.sidebar.header("🛠️ 위험 시설물 신고")
st.sidebar.caption("발견하신 위험 요소를 행정실로 즉시 전달합니다.")
with st.sidebar.form("report_form", clear_on_submit=True):
    uploaded_photo = st.file_uploader("현장 사진 업로드", type=['png', 'jpg', 'jpeg'])
    danger_opinion = st.text_area("어떤 점이 위험한가요?", placeholder="예: 체육관 입구 바닥 타일이 깨져서 학생들이 걸려 넘어질 위험이 있습니다.")
    
    submitted = st.form_submit_button("신고 등록")
    
    if submitted:
        if not danger_opinion.strip():
            st.sidebar.error("위험 요소에 대한 의견을 작성해주세요.")
        else:
            # 새로운 신고 내역을 세션에 추가
            new_report = {
                "id": len(st.session_state.board_data) + 1,
                "photo": uploaded_photo,
                "opinion": danger_opinion,
                "status": "등록", # 기본 상태
                "feedback": ""    # 행정실 피드백 초기값
            }
            st.session_state.board_data.append(new_report)
            st.sidebar.success("성공적으로 접수되었습니다.")

# 4. 선택한 조건으로 데이터 필터링
filtered_df = df[(df['학교급'] == school_level) & 
                 (df['사고시간'] == time_category) & 
                 (df['사고장소'] == location)]

# 💡 사고형태별 맞춤형 조치 및 병원 안내 단어장
action_guide = {
    "움직이는 물체와의 부딪힘": "🧊 [초기 조치] 타박상 부위 붓기를 확인하고 즉시 냉찜질을 해주세요. 출혈 시 깨끗한 천으로 지혈하세요.\n🏥 [추천 병원] 뼈 통증 호소 시 인근 정형외과 내원",
    "고정된 물체와의 부딪힘": "⚠️ [초기 조치] 머리를 부딪힌 경우 구토나 어지럼증이 없는지 꼭 관찰해야 합니다.\n🏥 [추천 병원] 충격이 크거나 의식 저하 시 충남대학교병원 등 종합병원 응급실",
    "사람과의 부딪힘": "🤝 [초기 조치] 양측 학생의 부상 부위를 모두 확인하고, 특히 치아나 안면부 손상 여부를 꼼꼼히 체크하세요.\n🏥 [추천 병원] 치아 손상 시 인근 치과, 안면부 타박상 시 정형외과/성형외과",
    "교통사고": "🚨 [초기 조치] 환자를 섣불리 이동시키지 말고 즉시 119에 신고하세요.\n📞 [신고처] 119 및 학교 전담 경찰관(SPO) 연락, 유성선병원 응급의료센터 등 이송",
    "물체 사이에 끼임/눌림": "🛑 [초기 조치] 억지로 빼내려 하지 말고, 주변 장치(문, 기계 등)의 동력을 즉시 차단하세요.\n📞 [신고처] 119 구조대 및 교내 시설관리팀",
    "사람 사이에 끼임/눌림": "🛑 [초기 조치] 즉시 주변 학생들을 해산시켜 공간과 호흡할 공기를 확보하세요.\n🏥 [추천 병원] 호흡 곤란 지속 시 즉시 119 신고",
    "넘어짐": "🩹 [초기 조치] 관절을 무리하게 움직이지 말고 보건실에서 냉찜질을 해주세요.\n🏥 [추천 병원] 골절이나 심한 삠 의심 시 유성구 인근 정형외과",
    "1미터 미만의 높이에서 떨어짐": "⚠️ [초기 조치] 찰과상을 소독하고 관절 통증 및 머리 부딪힘 여부를 체크하세요.\n🏥 [추천 병원] 통증 지속 시 정형외과 내원",
    "1미터 이상의 높이에서 떨어짐": "🚑 [초기 조치] 목이나 척추 손상 우려가 있으므로 절대 환자를 들어 옮기지 말고 즉시 119를 부르세요!\n🏥 [추천 병원] 119 판단하에 권역외상센터(건양대병원/을지대병원) 이송",
    "이동 중 충격을 가함": "🧊 [초기 조치] 통증 부위를 확인하고 가벼운 타박상은 냉찜질을 실시하세요.\n🏥 [추천 병원] 인근 정형외과",
    "스포츠 활동 중 충격을 가함": "🚑 [초기 조치] 머리나 목 부위 충격이라면 환자를 절대 이동시키지 마세요.\n📞 [신고처] 119 및 교내 보건실 즉시 연락",
    "물건을 운반하는 중 충격을 가함": "🩹 [초기 조치] 발등이나 손가락 찍힘을 확인하고, 부종 발생 시 즉시 냉찜질하세요.\n🏥 [추천 병원] 인근 정형외과 의원",
    "긁힘, 찔림": "🩸 [초기 조치] 흐르는 물에 상처 부위를 세척 후 소독하고 밴드를 붙여주세요.\n🏥 [추천 병원] 녹슨 못이나 날카로운 것에 깊게 찔린 경우 파상풍 주사를 위해 내과/정형외과 내원",
    "베임, 절단": "🩸 [초기 조치] 깨끗한 거즈로 직접 압박하여 지혈하세요. 절단 사고 시 절단 부위를 깨끗한 천에 싸서 비닐로 밀봉 후 얼음물에 담아 이동해야 합니다.\n🚑 [추천 병원] 수지접합 전문병원 또는 종합병원 응급실 즉시 이송",
    "동물에게 물림(사람 포함)": "🧼 [초기 조치] 흐르는 물과 비누로 상처를 5분 이상 충분히 씻어내세요.\n🏥 [추천 병원] 파상풍 및 감염 예방을 위해 즉시 인근 외과 또는 응급실 내원",
    "곤충,식물 등에 쏘임": "🐝 [초기 조치] 벌침이 보이면 손으로 뽑지 말고 신용카드 등으로 밀어서 제거 후 얼음찜질하세요.\n🏥 [추천 병원] 두드러기나 호흡곤란(아나필락시스) 발생 시 즉시 119 신고",
    "고온의 물체,물질 접촉/흡입/섭취": "🚰 [초기 조치] 10~15분간 흐르는 시원한 물로 화상 부위를 식혀주세요. (얼음 직접 접촉 금지, 물집 터뜨리기 금지)\n🏥 [추천 병원] 인근 화상 치료 가능 피부과/외과 또는 베스티안병원 같은 화상전문병원 내원",
    "일사병, 열사병": "💦 [초기 조치] 시원한 곳으로 이동 후 옷을 헐렁하게 하고, 의식이 있을 때만 물을 마시게 하세요.\n🚑 [추천 병원] 의식이 없거나 체온이 떨어지지 않으면 즉시 119 신고",
    "감전": "⚡ [초기 조치] 맨손으로 환자 접촉 절대 금지! 전원이나 차단기부터 먼저 내리세요.\n🚑 [추천 병원] 겉보기에 괜찮아도 심장 및 내장 손상 우려가 있으므로 즉시 응급실 내원",
    "주위에 장시간 노출": "🌡️ [초기 조치] 체온 유지(추울 땐 담요, 더울 땐 그늘) 및 안정을 취하게 하세요.\n🏥 [추천 병원] 의식 저하 시 119 신고 및 응급실 이송",
    "저온의 물체(드라이아이스 등) 물질 접촉": "❄️ [초기 조치] 동상 부위를 따뜻한 물(37~39도)에 20~30분간 담가 녹여주세요. 절대 문지르지 마세요.\n🏥 [추천 병원] 피부과 또는 외과 내원",
    "화학물질 접촉/흡입/섭취": "🧪 [초기 조치] 피부 접촉 시 흐르는 물에 15분 이상 세척하세요. 섭취 시 절대 억지로 토하게 하면 안 됩니다!\n📞 [신고처] 119 및 독성물질 국가정보센터 신고 후 물질 정보(MSDS) 지참하여 응급실 이송",
    "익사, 익수": "🏊‍♂️ [초기 조치] 구조 후 의식과 호흡을 확인하고, 필요시 심폐소생술(CPR)을 즉각 실시하세요.\n🚑 [추천 병원] 119 신고 후 즉시 종합병원 응급실 이송",
    "이물질에 의한 질식": "컥컥 [초기 조치] 기침을 유도하고, 안 되면 등 두드리기와 하임리히법을 즉시 교대로 실시하세요.\n🚑 [추천 병원] 골든타임이 중요하므로 발견 즉시 119 신고",
    "기타 호흡 곤란": "😮‍💨 [초기 조치] 편안한 자세(반좌위)를 유지하게 하고 꽉 낀 옷을 느슨하게 풀어주세요.\n🚑 [추천 병원] 평소 천식/알레르기 질환 여부 확인 후 즉시 119 신고",
    "식중독": "🤢 [초기 조치] 구토/설사 시 탈수 방지를 위해 수분을 섭취하게 하고, 남은 음식물을 보존하세요.\n🏥 [추천 병원] 인근 내과/소아청소년과 내원 및 관할 보건소 신고",
    "이물질 섭취로 인한 질병": "💊 [초기 조치] 섭취한 이물질 종류와 양 파악하세요. 억지로 토하게 하지 마세요.\n🏥 [추천 병원] 즉시 내과 및 응급실 내원 (건전지, 자석 섭취는 초응급 상황입니다)",
    "이물질 접촉에 의한 피부염": "🧴 [초기 조치] 원인 물질을 제거하고 흐르는 물에 세척하세요. 긁지 않도록 지도합니다.\n🏥 [추천 병원] 인근 피부과 의원 내원",
    "그밖의 손상 사고": "❗ [초기 조치] 보건실에 즉시 연락하여 상황을 알리고 필요시 초기 상태를 사진으로 남겨두세요.\n🏥 [추천 병원] 증상과 부위에 따라 적절한 인근 병의원 내원"
}

# 5. 메인 화면 - 기본 결과 띄우기
st.markdown("---")
st.write(f"**현재 상황:** {school_level} / {time_category} / {location}")
st.write(f"과거 동일 조건 사고 기록: 총 {len(filtered_df)}건")

if len(filtered_df) > 0:
    top_accidents = filtered_df['사고형태'].value_counts().head(3)
    
    st.markdown("### 🚨 가장 주의해야 할 사고 Top 3 및 대처 방안")
    for i, (accident, count) in enumerate(top_accidents.items(), 1):
        
        guide_text = action_guide.get(accident, "❗ 보건실에 즉시 연락하여 상황을 알리세요.")
        
        if i == 1:
            st.error(f"**1순위: {accident}** (발생 건수: {count}건)")
            st.info(guide_text) 
        elif i == 2:
            st.warning(f"**2순위: {accident}** (발생 건수: {count}건)")
            st.info(guide_text)
        elif i == 3:
            st.success(f"**3순위: {accident}** (발생 건수: {count}건)")
            st.info(guide_text)
            
    # 6. 심층 데이터 분석 시각화
    st.markdown("---")
    st.markdown("### 📊 [심층 분석] 해당 조건의 사고 특성 프로파일링")
    st.caption("과거 데이터를 바탕으로 도출된 통계입니다. 안전 지도 및 예산 편성에 활용하십시오.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🧑‍🎓 가장 취약한 학년 Top 5**")
        df1 = filtered_df['사고자학년'].dropna().value_counts().head(5).reset_index()
        df1.columns = ['항목', '건수']
        chart1 = alt.Chart(df1).mark_bar().encode(
            x=alt.X('건수:Q', title=None),
            y=alt.Y('항목:N', sort='-x', title=None) 
        )
        st.altair_chart(chart1, use_container_width=True)
        
    with col2:
        st.markdown("**🩹 주로 다치는 부위 Top 5**")
        df2 = filtered_df['사고부위'].dropna().value_counts().head(5).reset_index()
        df2.columns = ['항목', '건수']
        chart2 = alt.Chart(df2).mark_bar().encode(
            x=alt.X('건수:Q', title=None),
            y=alt.Y('항목:N', sort='-x', title=None)
        )
        st.altair_chart(chart2, use_container_width=True)
        
    with col3:
        st.markdown("**🏃‍♂️ 사고 당시 활동 Top 5**")
        df3 = filtered_df['사고당시활동'].dropna().value_counts().head(5).reset_index()
        df3.columns = ['항목', '건수']
        chart3 = alt.Chart(df3).mark_bar().encode(
            x=alt.X('건수:Q', title=None),
            y=alt.Y('항목:N', sort='-x', title=None)
        )
        st.altair_chart(chart3, use_container_width=True)

else:
    st.info("선택하신 조건에 해당하는 과거 사고 기록이 없습니다.")

# 7. [추가] 위험 시설물 신고 게시판 현황
st.markdown("---")
st.markdown("### 📢 위험 시설물 신고 및 조치 현황 게시판")
st.caption("현장에서 접수된 위험 요소와 행정실의 처리 진행 상태를 실시간으로 공유합니다.")

if not st.session_state.board_data:
    st.info("현재 접수된 신고 건이 없습니다.")
else:
    # 게시판 내역 출력 (최신 신고가 위로 오게 역순 정렬)
    for report in reversed(st.session_state.board_data):
        with st.container():
            col_img, col_desc = st.columns([1, 3])
            
            # 사진 출력 (첨부된 경우)
            with col_img:
                if report['photo'] is not None:
                    st.image(report['photo'], use_column_width=True)
                else:
                    st.write("📷 첨부 사진 없음")
            
            # 신고 내용 및 상태 라벨
            with col_desc:
                st.markdown(f"**📌 신고 내용 (No.{report['id']})**")
                st.write(report['opinion'])
                
                # 상태에 따라 뱃지 색상 다르게 표시
                if report['status'] == "등록":
                    st.markdown("🔹 **상태:** `등록 (대기중)`")
                elif report['status'] == "진행중":
                    st.markdown("🏃‍♂️ **상태:** `조치 진행중`")
                elif report['status'] == "완료":
                    st.markdown("✅ **상태:** `조치 완료`")
                
                # 피드백 내용 표시
                if report['feedback']:
                    st.success(f"**행정실 피드백:** {report['feedback']}")
                else:
                    st.warning("아직 행정실 피드백이 등록되지 않았습니다.")
                
                # [관리자(행정실)용 피드백 입력 폼]
                with st.expander("🛠️ 행정실 상태 업데이트 (관리자 전용)"):
                    new_status = st.radio("진행 상태 변경", ["등록", "진행중", "완료"], 
                                          index=["등록", "진행중", "완료"].index(report['status']), 
                                          key=f"status_{report['id']}")
                    new_feedback = st.text_area("피드백 작성", value=report['feedback'], key=f"fb_{report['id']}")
                    
                    if st.button("수정 내용 저장", key=f"btn_{report['id']}"):
                        # 세션 내 해당 데이터 업데이트
                        for item in st.session_state.board_data:
                            if item['id'] == report['id']:
                                item['status'] = new_status
                                item['feedback'] = new_feedback
                        st.rerun() # 수정 후 화면 즉시 새로고침
        st.markdown("---")