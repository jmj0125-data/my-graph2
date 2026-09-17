import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "해당 기간에 개봉한 216편의 영화 데이터를 살펴봅니다."
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일을 문자열로 변환
    df["openDt"] = df["openDt"].astype(str).str.zfill(8)

    # 여러 장르가 세로막대(|)로 연결되어 있다면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열 변환
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


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
st.success(f"총 {len(df):,}편의 영화 데이터를 불러왔습니다.")


# --------------------------------------------------
# 그래프 1
# 장르별 영화 편수 - 도넛 그래프
# --------------------------------------------------
st.divider()

st.header("그래프 1. 장르별 영화 편수")
st.caption("장르별로 영화가 몇 편씩 있는지 한눈에 비교합니다.")


genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화편수"]


fig = px.pie(
    genre_count,
    names="장르",
    values="영화편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    margin=dict(t=70, b=30, l=30, r=30),
    legend_title_text="장르"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 알 수 있는 것 입력 구역
# --------------------------------------------------
st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder="예: 이 기간에는 ○○ 장르의 영화가 가장 많이 개봉했다.",
    height=80,
    key="graph1_note"
)


# --------------------------------------------------
# 그래프 구역 종료
# --------------------------------------------------
st.divider()

st.caption("💡 도넛 조각에 마우스를 올리면 장르별 영화 편수와 전체에서 차지하는 비율을 확인할 수 있습니다.")
