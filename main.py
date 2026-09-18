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

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자 → 날짜
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# =======================================
# 데이터
# =======================================
st.subheader("데이터")
st.write(f"총 {len(df):,}편의 영화가 있습니다.")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)


# =======================================
# 그래프 1. 장르별 영화 편수
# =======================================
st.divider()
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
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(height=550)

st.plotly_chart(fig1, width="stretch")

st.info("이 그래프로 알 수 있는 것: ________________________________")


# =======================================
# 그래프 2. 장르별 영화별 총 관객 트리맵
# =======================================
st.divider()
st.subheader("2. 장르별 영화의 총 관객")

treemap_data = (
    df.groupby(["genre", "movieNm"], as_index=False)["total_audi"]
    .sum()
)

treemap_data = treemap_data[
    treemap_data["total_audi"].notna()
    & (treemap_data["total_audi"] > 0)
]

fig2 = px.treemap(
    treemap_data,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르 안의 영화별 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(height=700)

st.plotly_chart(fig2, width="stretch")

st.info("이 그래프로 알 수 있는 것: ________________________________")


# =======================================
# 그래프 3. 총 관객 히스토그램
# =======================================
st.divider()
st.subheader("3. 영화별 총 관객 분포")

hist_data = df[
    df["total_audi"].notna()
    & (df["total_audi"] > 0)
].copy()

fig3 = px.histogram(
    hist_data,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 분포",
    labels={"total_audi": "총 관객"}
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객",
    yaxis_title="영화 수"
)

st.plotly_chart(fig3, width="stretch")

# 가장 많이 몰려 있는 구간
min_audi = hist_data["total_audi"].min()
max_audi = hist_data["total_audi"].max()

if max_audi > min_audi:
    bin_width = (max_audi - min_audi) / 30

    hist_data["구간"] = (
        ((hist_data["total_audi"] - min_audi) / bin_width)
        .astype(int)
        .clip(upper=29)
    )

    most_common_bin = hist_data["구간"].value_counts().idxmax()

    range_start = min_audi + most_common_bin * bin_width
    range_end = range_start + bin_width

    st.markdown(
        f"""
**대부분의 영화가 몰려 있는 구간:**  
약 **{range_start:,.0f}명 ~ {range_end:,.0f}명**
"""
    )

max_movie = hist_data.loc[hist_data["total_audi"].idxmax()]

st.markdown(
    f"""
**가장 관객이 많은 영화:**  
**{max_movie["movieNm"]}** — **{max_movie["total_audi"]:,.0f}명**
"""
)

st.info("이 그래프로 알 수 있는 것: ________________________________")


# =======================================
# 그래프 4. 개봉일 스크린수와 총 관객의 관계
# =======================================
st.divider()
st.subheader("4. 개봉일 스크린수와 총 관객의 관계")

scatter_data = df[
    df["first_scrn"].notna()
    & df["total_audi"].notna()
    & (df["first_scrn"] > 0)
    & (df["total_audi"] > 0)
].copy()

fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre": "장르"
    },
    title="개봉일 스크린수와 총 관객의 관계"
)

fig4.update_traces(
    marker=dict(
        size=9,
        opacity=0.75
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객"
)

st.plotly_chart(fig4, width="stretch")

st.info("이 그래프로 알 수 있는 것: ________________________________")


# =======================================
# 그래프 5. 장르별 총 관객 박스플롯
# =======================================
st.divider()
st.subheader("5. 장르별 총 관객 분포")

# 유효한 총 관객 데이터만 사용
box_data = df[
    df["total_audi"].notna()
    & (df["total_audi"] >= 0)
].copy()

# 영화 수가 10편 이상인 장르만 선택
genre_counts = box_data["genre"].value_counts()

valid_genres = genre_counts[
    genre_counts >= 10
].index

box_data = box_data[
    box_data["genre"].isin(valid_genres)
].copy()

fig5 = px.box(
    box_data,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    labels={
        "genre": "장르",
        "total_audi": "총 관객"
    },
    title="영화가 10편 이상인 장르의 총 관객 분포"

# =======================================
# 그래프 6. 개봉일 스크린수와 총 관객의 버블 그래프
# =======================================
st.divider()
st.subheader("6. 개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블")

bubble_data = df[
    df["first_scrn"].notna()
    & df["total_audi"].notna()
    & df["first_week_audi"].notna()
    & (df["first_scrn"] > 0)
    & (df["total_audi"] > 0)
    & (df["first_week_audi"] > 0)
].copy()

fig6 = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=45,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre": "장르"
    },
    title="개봉일 스크린수와 총 관객의 관계 - 첫 주 관객을 버블 크기로 표현"
)

fig6.update_traces(
    marker=dict(
        opacity=0.7
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{customdata[0]}<br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명"
        "<extra></extra>"
    ),
    customdata=bubble_data[["genre"]]
)

fig6.update_layout(
    height=700,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객"
)

st.plotly_chart(
    fig6,
    width="stretch"
)

st.info("이 그래프로 알 수 있는 것: ________________________________")
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{x}<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    height=650,
    xaxis_title="장르",
    yaxis_title="총 관객"
)

st.plotly_chart(fig5, width="stretch")

st.info("이 그래프로 알 수 있는 것: ________________________________")

# =======================================
# 그래프 7. 제작 국가 → 장르 선버스트
# =======================================
st.divider()
st.subheader("7. 제작 국가에서 장르로 내려가는 영화 분포")

sunburst_data = df[
    df["nation"].notna()
    & (df["nation"].astype(str).str.strip() != "")
    & df["genre"].notna()
    & (df["genre"].astype(str).str.strip() != "")
].copy()

# 제작 국가와 장르별 영화 편수 계산
sunburst_data = (
    sunburst_data
    .groupby(["nation", "genre"], as_index=False)
    .agg(영화편수=("movieNm", "count"))
)

fig7 = px.sunburst(
    sunburst_data,
    path=["nation", "genre"],
    values="영화편수",
    title="제작 국가 → 장르별 영화 편수",
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "전체 비율: %{percentRoot:.1%}"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700
)

st.plotly_chart(
    fig7,
    width="stretch"
)

st.info("이 그래프로 알 수 있는 것: ________________________________")
