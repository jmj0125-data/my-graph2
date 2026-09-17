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

    # 장르: 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르는 기타로 처리
    df.loc[df["genre"] == "", "genre"] = "기타"

    # 숫자형으로 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================

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
    title="장르별 영화 편수"
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

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것:**")
st.text_input(
    "그래프 1 설명",
    key="graph1_note",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    label_visibility="collapsed"
)


# ==================================================
# 그래프 2. 장르별 영화 총 관객 트리맵
# ==================================================

st.markdown("---")
st.subheader("2. 장르 안에 들어 있는 영화")

# 트리맵에 사용할 데이터
treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].copy()

# 영화명이 없는 경우 제거
treemap_df = treemap_df[
    treemap_df["movieNm"].notna() &
    (treemap_df["movieNm"].astype(str).str.strip() != "")
]

# 같은 영화가 여러 번 있을 경우 총 관객 합계
treemap_df = (
    treemap_df
    .groupby(["genre", "movieNm"], as_index=False)["total_audi"]
    .sum()
)

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig2, width="stretch")

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것:**")
st.text_input(
    "그래프 2 설명",
    key="graph2_note",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    label_visibility="collapsed"
)
