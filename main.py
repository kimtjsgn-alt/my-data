with tab1:
  st.markdown("#### 📝 일별 원본 데이터 기술 통계 (Summary Statistics)")
  st.caption(
      "선택한 연도 범위 내 전체 일별 기온 데이터의 요약 통계입니다. (행: 통계 항목, 열:"
      " 기온 항목)"
  )

  # 일별 데이터 요약통계 계산 후 전치(Transpose) - .T 적용 해제 및 인덱스 이름 변경
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

  # 각 행별 단위 및 포맷팅 처리
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
