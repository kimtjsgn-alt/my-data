import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화 분석", page_icon="🌡️", layout="wide"
)

# 제목 및 설명
st.title("🌡️ 지난 100년간 서울의 기온은 어떻게 바뀌었을까?")
st.markdown(
    "본 애플리케이션은 기상청 서울 관측 데이터(seoul.csv)를 바탕으로 지난 100여 년간의 연평균"
    " 기온 변화 추이를 분석합니다."
)


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
  try:
    df = pd.read_csv(url, encoding="cp949")
  except Exception:
    df = pd.read_csv(url, encoding="utf-8")

  # 컬럼명 공백 제거
  df.columns = df.columns.str.strip()

  # 컬럼명 표준화 (괄호 등 제거 대응)
  col_map = {}
  for col in df.columns:
    if "날짜" in col:
      col_map[col] = "날짜"
    elif "지점" in col:
      col_map[col] = "지점"
    elif "평균" in col:
      col_map[col] = "평균기온"
    elif "최저" in col:
      col_map[col] = "최저기온"
    elif "최고" in col:
      col_map[col] = "최고기온"
  df = df.rename(columns=col_map)

  # 날짜 데이터 처리
  df["날짜"] = pd.to_datetime(df["날짜"])
  df["연도"] = df["날짜"].dt.year

  # 기온 데이터 수치형 변환
  numeric_cols = ["평균기온", "최저기온", "최고기온"]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce")

  df = df.dropna(subset=["평균기온"])
  return df


with st.spinner("데이터를 불러오는 중입니다..."):
  df = load_data()

# 사이드바 설정
st.sidebar.header("🔍 데이터 필터 및 옵션")

min_year = int(df["연도"].min())
max_year = int(df["연도"].max())

year_range = st.sidebar.slider(
    "조회 연도 범위 선택",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

window_size = st.sidebar.slider(
    "이동평균(Moving Average) 구간 (년)", min_value=1, max_value=20, value=10
)

# 선택된 연도 범위로 데이터 필터링
filtered_df = df[(df["연도"] >= year_range[0]) & (df["연도"] <= year_range[1])]

# 연도별 집계 (최소 300일 이상 관측된 해)
year_counts = filtered_df.groupby("연도")["평균기온"].count()
valid_years = year_counts[year_counts >= 300].index

annual_df = (
    filtered_df[filtered_df["연도"].isin(valid_years)]
    .groupby("연도")
    .agg(
        연평균기온=("평균기온", "mean"),
        연평균최저기온=("최저기온", "mean"),
        연평균최고기온=("최고기온", "mean"),
        연최고기온=("최고기온", "max"),
        연최저기온=("최저기온", "min"),
    )
    .reset_index()
)

# 이동평균 계산
annual_df[f"{window_size}년 이동평균"] = (
    annual_df["연평균기온"].rolling(window=window_size, min_periods=1).mean()
)

# 주요 지표 요약 (Metrics)
st.subheader("📌 주요 기온 통계 요약")
col1, col2, col3, col4 = st.columns(4)

if not annual_df.empty:
  first_temp = annual_df["연평균기온"].iloc[0]
  last_temp = annual_df["연평균기온"].iloc[-1]
  hottest_year = annual_df.loc[annual_df["연평균기온"].idxmax()]
  coldest_year = annual_df.loc[annual_df["연평균기온"].idxmin()]

  col1.metric(
      "최초 관측 연도 평균",
      f"{first_temp:.1f} °C",
      f"{annual_df['연도'].iloc[0]}년",
  )
  col2.metric(
      "최근 관측 연도 평균",
      f"{last_temp:.1f} °C",
      f"{annual_df['연도'].iloc[-1]}년",
  )
  col3.metric(
      "가장 뜨거웠던 해",
      f"{hottest_year['연평균기온']:.1f} °C",
      f"{int(hottest_year['연도'])}년",
  )
  col4.metric(
      "가장 추웠던 해",
      f"{coldest_year['연평균기온']:.1f} °C",
      f"{int(coldest_year['연도'])}년",
  )

st.markdown("---")

# 메인 그래프
st.subheader("📈 연평균 기온 변화 추이")

fig = go.Figure()

# 연평균기온 선 그래프
fig.add_trace(
    go.Scatter(
        x=annual_df["연도"],
        y=annual_df["연평균기온"],
        mode="lines+markers",
        name="연평균 기온",
        line=dict(color="#ff7f0e", width=2),
        marker=dict(size=5),
        hovertemplate="%{x}년: %{y:.2f}°C<extra></extra>",
    )
)

# 이동평균 선 그래프
fig.add_trace(
    go.Scatter(
        x=annual_df["연도"],
        y=annual_df[f"{window_size}년 이동평균"],
        mode="lines",
        name=f"{window_size}년 이동평균",
        line=dict(color="#d62728", width=3, dash="dash"),
        hovertemplate="%{x}년 (%{text}): %{y:.2f}°C<extra></extra>",
        text=[f"{window_size}년 이동평균"] * len(annual_df),
    )
)

# 추세선 (선형 회귀선)
if len(annual_df) > 1:
  z = np.polyfit(annual_df["연도"], annual_df["연평균기온"], 1)
  p = np.poly1d(z)
  fig.add_trace(
      go.Scatter(
          x=annual_df["연도"],
          y=p(annual_df["연도"]),
          mode="lines",
          name="선형 추세선",
          line=dict(color="#1f77b4", width=2, dash="dot"),
          hoverinfo="skip",
      )
  )

fig.update_layout(
    title=dict(
        text=f"서울 연도별 평균 기온 ({year_range[0]}년 ~ {year_range[1]}년)",
        font=dict(size=18),
    ),
    xaxis_title="연도",
    yaxis_title="기온 (°C)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

# 데이터 분석 및 요약 통계 탭 생성 (오류 해결 포인트: tab1, tab2, tab3을 먼저 선언)
st.subheader("📊 데이터 분석 및 요약 통계")
tab1, tab2, tab3 = st.tabs(
    ["📋 원본데이터 요약 통계", "🌡️ 최저/최고 기온 범위", "📑 연도별 데이터 테이블"]
)

with tab1:
  st.markdown("#### 📝 일별 원본 데이터 기술 통계 (Summary Statistics)")
  st.caption(
      "선택한 연도 범위 내 전체 일별 기온 데이터의 요약 통계입니다. (행: 통계 항목, 열:"
      " 기온 항목)"
  )

  # 일별 데이터 요약통계 계산 후 전치(Transpose)
  raw_stats = filtered_df[["평균기온", "최저기온", "최고기온"]].describe()
  raw_stats = raw_stats.rename(
      index={
          "count": "데이터 개수(일)",
          "mean": "평균",
          "std": "표준편차",
          "min": "최소값",
          "25%": "1사분위수(25%)",
          "50%": "중앙값(50%)",
          "75%": "3사분위수(75%)",
          "max": "최대값",
      }
  )

  formatted_raw_stats = raw_stats.copy().astype(object)
  for col in formatted_raw_stats.columns:
    formatted_raw_stats.loc["데이터 개수(일)", col] = (
        f"{raw_stats.loc['데이터 개수(일)', col]:,.0f}"
    )
    formatted_raw_stats.loc["평균", col] = f"{raw_stats.loc['평균', col]:.2f} °C"
    formatted_raw_stats.loc["표준편차", col] = (
        f"{raw_stats.loc['표준편차', col]:.2f}"
    )
    formatted_raw_stats.loc["최소값", col] = (
        f"{raw_stats.loc['최소값', col]:.1f} °C"
    )
    formatted_raw_stats.loc["1사분위수(25%)", col] = (
        f"{raw_stats.loc['1사분위수(25%)', col]:.1f} °C"
    )
    formatted_raw_stats.loc["중앙값(50%)", col] = (
        f"{raw_stats.loc['중앙값(50%)', col]:.1f} °C"
    )
    formatted_raw_stats.loc["3사분위수(75%)", col] = (
        f"{raw_stats.loc['3사분위수(75%)', col]:.1f} °C"
    )
    formatted_raw_stats.loc["최대값", col] = (
        f"{raw_stats.loc['최대값', col]:.1f} °C"
    )

  st.dataframe(formatted_raw_stats, use_container_width=True)

  st.markdown("---")
  st.markdown("#### 📅 연도별 집계 데이터 기술 통계")
  st.caption(
      "선택한 연도 범위 내 연도별 집계 지표(연평균, 연최고, 연최저)에 대한 요약"
      " 통계입니다. (행: 통계 항목, 열: 기온 항목)"
  )

  annual_stats = annual_df[
      ["연평균기온", "연평균최저기온", "연평균최고기온", "연최고기온", "연최저기온"]
  ].describe()
  annual_stats = annual_stats.rename(
      index={
          "count": "연도 수(개)",
          "mean": "평균",
          "std": "표준편차",
          "min": "최소값",
          "25%": "1사분위수(25%)",
          "50%": "중앙값(50%)",
          "75%": "3사분위수(75%)",
          "max": "최대값",
      }
  )

  formatted_annual_stats = annual_stats.copy().astype(object)
  for col in formatted_annual_stats.columns:
    formatted_annual_stats.loc["연도 수(개)", col] = (
        f"{annual_stats.loc['연도 수(개)', col]:,.0f}"
    )
    formatted_annual_stats.loc["평균", col] = (
        f"{annual_stats.loc['평균', col]:.2f} °C"
    )
    formatted_annual_stats.loc["표준편차", col] = (
        f"{annual_stats.loc['표준편차', col]:.2f}"
    )
    formatted_annual_stats.loc["최소값", col] = (
        f"{annual_stats.loc['최소값', col]:.1f} °C"
    )
    formatted_annual_stats.loc["1사분위수(25%)", col] = (
        f"{annual_stats.loc['1사분위수(25%)', col]:.1f} °C"
    )
    formatted_annual_stats.loc["중앙값(50%)", col] = (
        f"{annual_stats.loc['중앙값(50%)', col]:.1f} °C"
    )
    formatted_annual_stats.loc["3사분위수(75%)", col] = (
        f"{annual_stats.loc['3사분위수(75%)', col]:.1f} °C"
    )
    formatted_annual_stats.loc["최대값", col] = (
        f"{annual_stats.loc['최대값', col]:.1f} °C"
    )

  st.dataframe(formatted_annual_stats, use_container_width=True)

with tab2:
  fig_range = go.Figure()
  fig_range.add_trace(
      go.Scatter(
          x=annual_df["연도"],
          y=annual_df["연평균최고기온"],
          mode="lines",
          name="연평균 최고기온",
          line=dict(color="#ef553b"),
      )
  )
  fig_range.add_trace(
      go.Scatter(
          x=annual_df["연도"],
          y=annual_df["연평균기온"],
          mode="lines",
          name="연평균 기온",
          line=dict(color="#ffa15a"),
      )
  )
  fig_range.add_trace(
      go.Scatter(
          x=annual_df["연도"],
          y=annual_df["연평균최저기온"],
          mode="lines",
          name="연평균 최저기온",
          line=dict(color="#00cc96"),
      )
  )
  fig_range.update_layout(
      title="연도별 최고 / 평균 / 최저 기온 비교",
      xaxis_title="연도",
      yaxis_title="기온 (°C)",
      hovermode="x unified",
      template="plotly_white",
  )
  st.plotly_chart(fig_range, use_container_width=True)

with tab3:
  st.dataframe(
      annual_df.style.format({
          "연평균기온": "{:.2f} °C",
          "연평균최저기온": "{:.2f} °C",
          "연평균최고기온": "{:.2f} °C",
          "연최고기온": "{:.1f} °C",
          "연최저기온": "{:.1f} °C",
          f"{window_size}년 이동평균": "{:.2f} °C",
      }),
      use_container_width=True,
  )
