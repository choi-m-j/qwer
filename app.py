import streamlit as st
import pandas as pd
import altair as alt

# 1. 화면 기본 설정
st.set_page_config(page_title="선생님의 안전 나침반", layout="wide")
st.title("🧭 선생님의 안전 나침반")
st.subheader("데이터 융합을 통한 다방향 학교 안전사고 예측 대시보드")

if 'board_data' not in st.session_state:
    st.session_state.board_data = []

# 2. 통합 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv('total_accident_data.zip', compression='zip')

df = load_data()

# 3. 왼쪽 사이드바 (조건 입력)
st.sidebar.header("상황을 선택해주세요 👇")
school_level = st.sidebar.selectbox("학교급", df['학교급'].unique())
time_category = st.sidebar.selectbox("사고시간", df['사고시간'].unique())
location = st.sidebar.selectbox("사고장소", df['사고장소'].unique())

st.sidebar.markdown("---")

# 위험 시설물 신고 폼
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
            new_report = {
                "id": len(st.session_state.board_data) + 1,
                "photo": uploaded_photo,
                "opinion": danger_opinion,
                "status": "등록",
                "feedback": ""
            }
            st.session_state.board_data.append(new_report)
            st.sidebar.success("성공적으로 접수되었습니다.")

# 4. 데이터 필터링
filtered_df = df[(df['학교급'] == school_level) & 
                 (df['사고시간'] == time_category) & 
                 (df['사고장소'] == location)]

# 💡 사고형태별 조치 단어장
action_guide = {
    "움직이는 물체와의 부딪힘": "🧊 [초기 조치] 타박상 부위 붓기를 확인하고 즉시 냉찜질을 해주세요. 출혈 시 깨끗한 천으로 지혈하세요.\n🏥 [추천 병원] 뼈 통증 호소 시 인근 정형외과 내원",
    "고정된 물체와의 부딪힘": "⚠️ [초기 조치] 머리를 부딪힌 경우 구토나 어지럼증이 없는지 꼭 관찰해야 합니다.",
    "사람과의 부딪힘": "🤝 [초기 조치] 양측 학생의 부상 부위를 모두 확인하고, 특히 치아나 안면부 손상 여부를 꼼꼼히 체크하세요.",
    "교통사고": "🚨 [초기 조치] 환자를 섣불리 이동시키지 말고 즉시 119에 신고하세요.",
    "넘어짐": "🩹 [초기 조치] 관절을 무리하게 움직이지 말고 보건실에서 냉찜질을 해주세요.",
    "1미터 이상의 높이에서 떨어짐": "🚑 [초기 조치] 목이나 척추 손상 우려가 있으므로 절대 환자를 들어 옮기지 말고 즉시 119를 부르세요!",
    "스포츠 활동 중 충격을 가함": "🚑 [초기 조치] 머리나 목 부위 충격이라면 환자를 절대 이동시키지 마세요.",
    "화학물질 접촉/흡입/섭취": "🧪 [초기 조치] 피부 접촉 시 흐르는 물에 15분 이상 세척하세요. 섭취 시 절대 억지로 토하게 하면 안 됩니다!"
}

# 💡 [신규 추가] 부상 부위별 사전 응급처치 매뉴얼
first_aid_manual = {
    "머리": "🧠 [머리] 외상이 없어도 구토, 어지럼증, 기억상실 여부를 반드시 확인해야 합니다. 뇌진탕 의심 시 절대 안정을 취하고 활동을 즉시 중단시키세요.",
    "치아": "🦷 [치아] 부러지거나 빠진 치아는 건조해지지 않도록 우유나 생리식염수에 담가 30분 내로 치과에 가야 접합 확률이 높습니다.",
    "발목": "🦶 [발목] 발목을 삐었을 때 무리하게 걷게 하지 말고, 부상 부위를 심장보다 높게 올린 후 즉시 냉찜질을 적용하여 부기를 가라앉혀야 합니다.",
    "무릎": "🦵 [무릎] 찰과상은 흐르는 물에 이물질을 씻어내어 2차 감염을 막고, 타박상은 관절을 구부리지 않게 펴고 냉찜질을 실시하세요.",
    "손가락": "🖐️ [손가락] 삐거나 골절이 의심되면 관절을 억지로 펴거나 맞추려 하지 말고, 펜이나 아이스크림 막대 등을 부목으로 대어 고정하세요.",
    "손목": "🤚 [손목] 통증이 심할 경우 꺾이지 않게 책이나 널빤지로 받치고, 붓기 시작하면 압박을 막기 위해 시계나 팔찌를 즉시 제거해야 합니다.",
    "얼굴": "👤 [얼굴] 코피가 나면 고개를 뒤로 젖히지 말고 '앞으로' 약간 숙인 상태에서 콧방울을 5~10분간 강하게 압박해야 기도로 피가 넘어가지 않습니다.",
    "복합부위": "⚠️ [복합부위] 다발성 손상이나 척추 의심 사고 시, 2차 손상을 막기 위해 환자를 절대 함부로 이동시키지 말고 119를 즉시 호출하세요."
}

# 5. 메인 화면 출력
st.markdown("---")
st.write(f"**현재 상황:** {school_level} / {time_category} / {location}")
st.write(f"과거 동일 조건 사고 기록: 총 {len(filtered_df)}건")

if len(filtered_df) > 0:
    # 5-1. 사고 형태 Top 3
    top_accidents = filtered_df['사고형태'].value_counts().head(3)
    st.markdown("### 🚨 가장 주의해야 할 사고 Top 3 및 대처 방안")
    for i, (accident, count) in enumerate(top_accidents.items(), 1):
        guide_text = action_guide.get(accident, "❗ 보건실에 즉시 연락하여 상황을 알리세요.")
        if i == 1:
            st.error(f"**1순위: {accident}** ({count}건)\n\n{guide_text}")
        elif i == 2:
            st.warning(f"**2순위: {accident}** ({count}건)\n\n{guide_text}")
        elif i == 3:
            st.success(f"**3순위: {accident}** ({count}건)\n\n{guide_text}")

    # 5-2. [신규 추가] 활동 전 필수 숙지 응급처치
    st.markdown("---")
    st.markdown("### 🩺 활동 전 필수 숙지! 주요 부상 부위별 응급처치 매뉴얼")
    st.caption("선택하신 상황에서 가장 빈번하게 발생하는 부상 부위에 대한 핵심 사전 숙지 사항입니다.")
    
    top_body_parts = filtered_df['사고부위'].dropna().value_counts().head(3)
    
    col_fa1, col_fa2, col_fa3 = st.columns(3)
    fa_columns = [col_fa1, col_fa2, col_fa3]
    
    for i, (part, count) in enumerate(top_body_parts.items()):
        manual_text = first_aid_manual.get(part, f"[{part}] 손상 발생 시 즉시 보건교사에게 인계하여 상태를 확인하십시오.")
        with fa_columns[i]:
            st.info(f"**{part} ({count}건)**\n\n{manual_text}")
            
    # 6. 심층 데이터 시각화
    st.markdown("---")
    st.markdown("### 📊 [심층 분석] 해당 조건의 사고 특성 프로파일링")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🧑‍🎓 가장 취약한 학년 Top 5**")
        df1 = filtered_df['사고자학년'].dropna().value_counts().head(5).reset_index()
        df1.columns = ['항목', '건수']
        st.altair_chart(alt.Chart(df1).mark_bar().encode(x=alt.X('건수:Q', title=None), y=alt.Y('항목:N', sort='-x', title=None)), use_container_width=True)
        
    with col2:
        st.markdown("**🩹 주로 다치는 부위 Top 5**")
        df2 = filtered_df['사고부위'].dropna().value_counts().head(5).reset_index()
        df2.columns = ['항목', '건수']
        st.altair_chart(alt.Chart(df2).mark_bar().encode(x=alt.X('건수:Q', title=None), y=alt.Y('항목:N', sort='-x', title=None)), use_container_width=True)
        
    with col3:
        st.markdown("**🏃‍♂️ 사고 당시 활동 Top 5**")
        df3 = filtered_df['사고당시활동'].dropna().value_counts().head(5).reset_index()
        df3.columns = ['항목', '건수']
        st.altair_chart(alt.Chart(df3).mark_bar().encode(x=alt.X('건수:Q', title=None), y=alt.Y('항목:N', sort='-x', title=None)), use_container_width=True)

else:
    st.info("선택하신 조건에 해당하는 과거 사고 기록이 없습니다.")

# 7. 게시판 현황
st.markdown("---")
st.markdown("### 📢 위험 시설물 신고 및 조치 현황 게시판")

if not st.session_state.board_data:
    st.info("현재 접수된 신고 건이 없습니다.")
else:
    for report in reversed(st.session_state.board_data):
        with st.container():
            col_img, col_desc = st.columns([1, 3])
            
            with col_img:
                if report['photo'] is not None:
                    st.image(report['photo'], use_column_width=True)
                else:
                    st.write("📷 첨부 사진 없음")
            
            with col_desc:
                st.markdown(f"**📌 신고 내용 (No.{report['id']})**")
                st.write(report['opinion'])
                
                if report['status'] == "등록":
                    st.markdown("🔹 **상태:** `등록 (대기중)`")
                elif report['status'] == "진행중":
                    st.markdown("🏃‍♂️ **상태:** `조치 진행중`")
                elif report['status'] == "완료":
                    st.markdown("✅ **상태:** `조치 완료`")
                
                if report['feedback']:
                    st.success(f"**행정실 피드백:** {report['feedback']}")
                else:
                    st.warning("아직 행정실 피드백이 등록되지 않았습니다.")
                
                with st.expander("🛠️ 행정실 상태 업데이트 (관리자 전용)"):
                    new_status = st.radio("진행 상태 변경", ["등록", "진행중", "완료"], 
                                          index=["등록", "진행중", "완료"].index(report['status']), 
                                          key=f"status_{report['id']}")
                    new_feedback = st.text_area("피드백 작성", value=report['feedback'], key=f"fb_{report['id']}")
                    
                    if st.button("수정 내용 저장", key=f"btn_{report['id']}"):
                        for item in st.session_state.board_data:
                            if item['id'] == report['id']:
                                item['status'] = new_status
                                item['feedback'] = new_feedback
                        st.rerun()
        st.markdown("---")