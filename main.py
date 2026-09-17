import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 불러오기
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자를 날짜로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르: 세로막대(|)로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 비어 있는 장르는 기타로 처리
    df.loc[df["genre"] == "", "genre"] = "기타"

    return df


df = load_data()

# --------------------------------------------------
# 그래프 1. 장르별 영화 편수
# --------------------------------------------------

st.subheader("1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화편수",
    hole=0.5,
    title="장르별 영화 편수",
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    margin=dict(t=60, b=20, l=20, r=20),
    legend_title="장르"
)

st.plotly_chart(fig1, width="stretch")

# 그래프 설명 영역
st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것:**")
st.text_input(
    "내용을 입력하세요.",
    key="graph1_note",
    placeholder="예: 어떤 장르의 영화가 가장 많은지 알 수 있다.",
    label_visibility="collapsed"
)

st.markdown("---")
