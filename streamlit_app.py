
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# ==========================================
# 1. 데이터 불러오기
# ==========================================

# KPI 데이터
kpi_csv = """가입자,가입후30일첫주문,조회to장바구니,30일재주문율
"2,774",0.699,0.8413,0.674"""

kpi = pd.read_csv(io.StringIO(kpi_csv)).iloc[0]


# 월별 첫 주문 전환율 데이터
problem_csv = """가입월,가입자수,INSTA가입자,첫주문고객수,첫주문전환율
25.Sep,140,0,104,0.7429
25.Oct,149,0,113,0.7584
25.Nov,158,0,119,0.7532
25.Dec,167,0,128,0.7665
26.Jan,267,91,181,0.6779
26.Feb,285,100,194,0.6807
26.Mar,303,109,201,0.6634
26.Apr,310,107,216,0.6968
26.May,315,103,226,0.7175
26.Jun,342,121,217,0.6345
26.Jul,338,108,240,0.7101"""

problem = pd.read_csv(io.StringIO(problem_csv))

problem["가입월_날짜"] = pd.to_datetime(
    problem["가입월"], format="%y.%b"
)

problem = problem.sort_values(
    "가입월_날짜"
).reset_index(drop=True)

problem["월표시"] = problem["가입월_날짜"].dt.strftime("%y.%m")
problem["전환율"] = problem["첫주문전환율"] * 100
problem["x"] = range(len(problem))


# 캠페인별 조회 → 장바구니 전환 데이터
cause_csv = """캠페인구분,식당조회고객수,장바구니조회고객수,조회to장바구니
NAVER_검색광고,504,442,0.877
GOOGLE_앱설치,381,341,0.895
ORGANIC,814,721,0.8857
친구초대,263,229,0.8707
INSTA_첫주문쿠폰,704,510,0.7244"""

cause = pd.read_csv(io.StringIO(cause_csv))

cause["전환율"] = cause["조회to장바구니"] * 100

cause = cause.sort_values(
    "전환율", ascending=False
).reset_index(drop=True)


# 캠페인별 재주문 데이터
suggestion_csv = """캠페인구분,첫주문고객수,재주문고객수,재주문율
NAVER_검색광고,434,315,0.7258
GOOGLE_앱설치,319,232,0.7273
ORGANIC,695,511,0.7353
친구초대,216,167,0.7731
INSTA_첫주문쿠폰,456,203,0.4452"""

suggestion = pd.read_csv(io.StringIO(suggestion_csv))

suggestion["재주문율_표시"] = suggestion["재주문율"] * 100

suggestion = suggestion.sort_values(
    "재주문율_표시", ascending=False
).reset_index(drop=True)


# ==========================================
# 2. 공통 색상
# ==========================================
GRAY = "#A0A7B1"
DARK_RED = "#B42332"
DARK_GRAY = "#707780"
LIGHT_GRAY = "rgba(148, 163, 184, 0.12)"
GRID_COLOR = "#E9ECEF"

INSTA = "INSTA_첫주문쿠폰"


# ==========================================
# 3. 리포트 제목
# ==========================================
st.title("사용자 행동 분석 대시보드")

st.caption(
    "배달앱 신규 가입 고객 · 가입 후 30일 기준 · 2025.09~2026.07"
)


# ==========================================
# 4. 핵심 KPI 카드
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="가입 후 30일 이내 첫 주문 전환율",
        value=f"{kpi['가입후30일첫주문']:.1%}"
    )

with col2:
    st.metric(
        label="식당 조회 → 장바구니 전환율",
        value=f"{kpi['조회to장바구니']:.1%}"
    )

with col3:
    st.metric(
        label="첫 주문 후 30일 이내 재주문율",
        value=f"{kpi['30일재주문율']:.1%}"
    )


# ==========================================
# 5. 차트 1 - 월별 첫 주문 전환율 추이
# ==========================================
st.divider()

st.info(
    "2026년 1월 INSTA 첫주문쿠폰 캠페인 시작 이후 "
    "전체 첫 주문 전환율이 하락했다. "
    "2025년 12월 76.65%에서 2026년 1월 67.79%로 "
    "8.86%p 감소했다."
)

campaign_idx = problem.index[
    problem["가입월"] == "26.Jan"
][0]

fig1 = go.Figure()

# 캠페인 운영 기간 음영
fig1.add_vrect(
    x0=campaign_idx - 0.5,
    x1=len(problem) - 0.5,
    fillcolor=LIGHT_GRAY,
    opacity=1,
    line_width=0,
    layer="below"
)

# 전체 월별 추이
fig1.add_trace(
    go.Scatter(
        x=problem["x"],
        y=problem["전환율"],
        mode="lines+markers",
        name="첫 주문 전환율",
        line=dict(
            color=GRAY,
            width=2.5
        ),
        marker=dict(
            color=GRAY,
            size=8
        ),
        customdata=problem["월표시"],
        hovertemplate=(
            "가입월: %{customdata}<br>"
            "첫 주문 전환율: %{y:.1f}%"
            "<extra></extra>"
        )
    )
)

# 2025년 12월 → 2026년 1월 하락 구간 강조
highlight = problem.iloc[
    campaign_idx - 1:campaign_idx + 1
]

fig1.add_trace(
    go.Scatter(
        x=highlight["x"],
        y=highlight["전환율"],
        mode="lines",
        line=dict(
            color=DARK_RED,
            width=4
        ),
        showlegend=False,
        hoverinfo="skip"
    )
)

# 2026년 1월 데이터 포인트 강조
jan_rate = problem.loc[campaign_idx, "전환율"]

fig1.add_trace(
    go.Scatter(
        x=[campaign_idx],
        y=[jan_rate],
        mode="markers",
        marker=dict(
            color=DARK_RED,
            size=12,
            line=dict(color="white", width=2)
        ),
        showlegend=False,
        hovertemplate=(
            "2026.01<br>"
            "첫 주문 전환율: %{y:.1f}%"
            "<extra></extra>"
        )
    )
)

# 1월 전환율 라벨
fig1.add_annotation(
    x=campaign_idx,
    y=jan_rate,
    text=f"<b>{jan_rate:.1f}%</b>",
    showarrow=False,
    yshift=-24,
    font=dict(
        size=13,
        color=DARK_RED
    )
)

# 캠페인 시작 수직 점선
fig1.add_vline(
    x=campaign_idx,
    line_dash="dash",
    line_width=1.5,
    line_color=DARK_RED
)

# 캠페인 시작 주석
fig1.add_annotation(
    x=campaign_idx,
    y=0.98,
    xref="x",
    yref="paper",
    text="<b>INSTA 캠페인 시작 (2026.01)</b>",
    showarrow=False,
    xanchor="left",
    xshift=10,
    font=dict(
        size=12,
        color=DARK_RED
    ),
    bgcolor="rgba(255,255,255,0.85)"
)

fig1.update_layout(
    title=dict(
        text=(
            "월별 신규 가입 고객의 첫 주문 전환율 추이"
            " · 가입 후 30일 기준 · 2025.09~2026.07"
        ),
        font=dict(size=17)
    ),
    template="plotly_white",
    height=440,
    margin=dict(l=40, r=30, t=90, b=45),
    showlegend=False,
    hovermode="x unified",
    plot_bgcolor="white"
)

fig1.update_xaxes(
    title_text="가입월",
    tickmode="array",
    tickvals=problem["x"].tolist(),
    ticktext=problem["월표시"].tolist(),
    range=[-0.4, len(problem) - 0.5],
    showgrid=False,
    zeroline=False
)

fig1.update_yaxes(
    title_text="가입 후 30일 이내 첫 주문 전환율",
    ticksuffix="%",
    tickformat=".1f",
    range=[58, 80],
    dtick=5,
    showgrid=True,
    gridcolor=GRID_COLOR,
    zeroline=False
)

st.plotly_chart(fig1, width="stretch")


# ==========================================
# 6. 차트 2 - 캠페인별 장바구니 전환율 비교
# ==========================================
st.divider()

st.info(
    "INSTA 첫주문쿠폰 가입자의 조회 → 장바구니 전환율은 "
    "72.44%로, 다른 캠페인(87.07%-89.50%)보다 "
    "14.63%-17.06%p 낮아 주요 전환 병목으로 나타났다."
)

# INSTA 제외 캠페인 평균 (단순 산술평균)
other_avg = cause.loc[
    cause["캠페인구분"] != INSTA,
    "전환율"
].mean()

# INSTA만 진한 빨간색
bar_colors2 = [
    DARK_RED if name == INSTA else GRAY
    for name in cause["캠페인구분"]
]

# 툴팁용 식당 조회 고객 수
hover_n2 = [
    f"{n:,}"
    for n in cause["식당조회고객수"]
]

# 막대 끝 라벨
bar_labels2 = [
    f"{rate:.1f}%"
    for rate in cause["전환율"]
]

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=cause["전환율"],
        y=cause["캠페인구분"],
        orientation="h",
        marker=dict(
            color=bar_colors2
        ),
        width=0.55,
        text=bar_labels2,
        textposition="outside",
        textfont=dict(size=12),
        cliponaxis=False,
        customdata=hover_n2,
        hovertemplate=(
            "가입 캠페인: %{y}<br>"
            "조회 → 장바구니 전환율: %{x:.1f}%<br>"
            "식당 조회 고객 수 (n): %{customdata}명"
            "<extra></extra>"
        ),
        showlegend=False
    )
)

# 다른 캠페인 평균 기준선
fig2.add_vline(
    x=other_avg,
    line_dash="dot",
    line_width=1.8,
    line_color=DARK_GRAY
)

# 기준선 주석
fig2.add_annotation(
    x=other_avg,
    y=1.10,
    xref="x",
    yref="paper",
    text=f"<b>기타 캠페인 평균 {other_avg:.1f}%</b>",
    showarrow=False,
    xanchor="center",
    font=dict(
        size=12,
        color=DARK_GRAY
    ),
    bgcolor="rgba(255,255,255,0.9)"
)

fig2.update_layout(
    title=dict(
        text=(
            "가입 캠페인별 식당 조회 → 장바구니 전환율 비교"
            " · 가입 후 30일 기준 · 2025.09~2026.07"
        ),
        font=dict(size=17)
    ),
    template="plotly_white",
    height=430,
    margin=dict(l=150, r=45, t=105, b=55),
    showlegend=False,
    plot_bgcolor="white",
    bargap=0.35
)

fig2.update_xaxes(
    title_text="식당 조회 → 장바구니 전환율",
    range=[0, 105],
    ticksuffix="%",
    tickformat=".1f",
    dtick=20,
    showgrid=True,
    gridcolor=GRID_COLOR,
    zeroline=False
)

fig2.update_yaxes(
    title_text="가입 캠페인",
    autorange="reversed",
    showgrid=False,
    zeroline=False
)

st.plotly_chart(fig2, width="stretch")


# ==========================================
# 7. 차트 3 - 캠페인별 30일 재주문율 비교
# ==========================================
st.divider()

st.info(
    "INSTA 첫주문쿠폰 가입자의 재주문율을 다른 캠페인과 "
    "비교하여 고객 유지 성과를 평가하고, "
    "재주문 유도를 위한 개선 우선순위를 선정할 필요가 있다."
)

# ------------------------------------------
# 전체 평균 재주문율
# 전체 재주문 고객 수 / 전체 첫 주문 고객 수
# 캠페인별 고객 규모를 반영한 가중평균
# ------------------------------------------
overall_reorder_rate = (
    suggestion["재주문고객수"].sum()
    / suggestion["첫주문고객수"].sum()
    * 100
)

# INSTA만 진한 빨간색, 나머지는 회색
bar_colors3 = [
    DARK_RED if name == INSTA else GRAY
    for name in suggestion["캠페인구분"]
]

# 막대 끝에 표시할 재주문율
bar_labels3 = [
    f"{rate:.1f}%"
    for rate in suggestion["재주문율_표시"]
]

# 툴팁용 고객 수 (천 단위 쉼표)
hover_data3 = [
    [f"{first:,}", f"{repeat:,}"]
    for first, repeat in zip(
        suggestion["첫주문고객수"],
        suggestion["재주문고객수"]
    )
]

fig3 = go.Figure()

# ------------------------------------------
# 캠페인별 가로 막대그래프
# ------------------------------------------
fig3.add_trace(
    go.Bar(
        x=suggestion["재주문율_표시"],
        y=suggestion["캠페인구분"],
        orientation="h",
        marker=dict(
            color=bar_colors3
        ),
        width=0.55,
        text=bar_labels3,
        textposition="outside",
        textfont=dict(size=12),
        cliponaxis=False,
        customdata=hover_data3,
        hovertemplate=(
            "가입 캠페인: %{y}<br>"
            "30일 이내 재주문율: %{x:.1f}%<br>"
            "첫 주문 고객 수 (n): %{customdata[0]}명<br>"
            "재주문 고객 수: %{customdata[1]}명"
            "<extra></extra>"
        ),
        showlegend=False
    )
)

# ------------------------------------------
# 전체 평균 재주문율 기준선
# ------------------------------------------
fig3.add_vline(
    x=overall_reorder_rate,
    line_dash="dot",
    line_width=1.8,
    line_color=DARK_GRAY
)

# 기준선 라벨 (add_annotation 별도 사용)
fig3.add_annotation(
    x=overall_reorder_rate,
    y=1.10,
    xref="x",
    yref="paper",
    text=(
        f"<b>전체 평균 재주문율 "
        f"{overall_reorder_rate:.1f}%</b>"
    ),
    showarrow=False,
    xanchor="center",
    font=dict(
        size=12,
        color=DARK_GRAY
    ),
    bgcolor="rgba(255,255,255,0.9)"
)

# ------------------------------------------
# 차트 레이아웃
# ------------------------------------------
fig3.update_layout(
    title=dict(
        text=(
            "가입 캠페인별 30일 이내 재주문율 비교"
            " · 첫 주문 고객 기준 · 2025.09~2026.07"
        ),
        font=dict(size=17)
    ),
    template="plotly_white",
    height=430,
    margin=dict(l=150, r=45, t=105, b=55),
    showlegend=False,
    plot_bgcolor="white",
    bargap=0.35
)

# x축: 재주문율 (0부터 시작)
fig3.update_xaxes(
    title_text="첫 주문 후 30일 이내 재주문율",
    range=[0, 100],
    ticksuffix="%",
    tickformat=".1f",
    dtick=20,
    showgrid=True,
    gridcolor=GRID_COLOR,
    zeroline=False
)

# y축: 가입 캠페인
# 재주문율 높은 순서로 위에서 아래 정렬
fig3.update_yaxes(
    title_text="가입 캠페인",
    autorange="reversed",
    showgrid=False,
    zeroline=False
)

st.plotly_chart(fig3, width="stretch")
