import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(page_title="관심지수 분석", page_icon="5️⃣", layout="wide")

# 환경 변수 로드
load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_video_trend_data():
    """영상 트렌드 데이터 로드"""
    client = get_supabase_client()
    
    # daily_video_trends 테이블 조회
    response = client.table("daily_video_trends")\
        .select("*")\
        .order("collected_date", desc=False)\
        .execute()
        
    if not response.data:
        return pd.DataFrame()
        
    df = pd.DataFrame(response.data)
    df['collected_date'] = pd.to_datetime(df['collected_date']).dt.date
    
    return df

df = load_video_trend_data()

if df.empty:
    st.info("아직 수집된 영상 트렌드 데이터가 없습니다.")
    st.stop()

# --- 헤더 ---
st.title("5️⃣ 관심지수 분석 (영상 트렌드)")
st.markdown("### 객관적 지표(조회수, 좋아요)를 통한 여론 관심도 분석")
st.markdown("---")

# 집계
daily_summary = df.groupby('collected_date').agg(
    video_count=('video_count', 'sum'),
    total_views=('total_views', 'sum'),
    total_likes=('total_likes', 'sum'),
    total_comments=('total_comments', 'sum')
).reset_index().sort_values('collected_date')

# 전일 대비 증감 계산
daily_summary['views_diff'] = daily_summary['total_views'].diff().fillna(0)
daily_summary['likes_diff'] = daily_summary['total_likes'].diff().fillna(0)
daily_summary['comments_diff'] = daily_summary['total_comments'].diff().fillna(0)
daily_summary['video_diff'] = daily_summary['video_count'].diff().fillna(0)

# 증감율 계산 (%)
daily_summary['views_rate'] = daily_summary['total_views'].pct_change().fillna(0) * 100
daily_summary['likes_rate'] = daily_summary['total_likes'].pct_change().fillna(0) * 100

# 날짜 문자열 변환 (Gapless 그래프용)
daily_summary['date_str'] = daily_summary['collected_date'].astype(str)

# --- 1. 핵심 KPI (최신 상태) ---
st.subheader("📊 최신 관심지표 현황")
latest = daily_summary.iloc[-1]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "총 영상 수", 
        f"{int(latest['video_count']):,}개", 
        f"{int(latest['video_diff']):+,}개"
    )

with kpi2:
    st.metric(
        "총 조회수", 
        f"{int(latest['total_views']):,}회", 
        f"{int(latest['views_diff']):+,}회"
    )

with kpi3:
    st.metric(
        "총 좋아요", 
        f"{int(latest['total_likes']):,}개", 
        f"{int(latest['likes_diff']):+,}개"
    )

with kpi4:
    st.metric(
        "총 댓글 수", 
        f"{int(latest['total_comments']):,}개", 
        f"{int(latest['comments_diff']):+,}개"
    )

st.markdown("---")

# --- 2. 수집일별 상세 통계 (테이블) ---
st.subheader("📑 수집일별 종합 통계")

# 보기 좋게 포맷팅
display_table = daily_summary.copy()
display_table = display_table.rename(columns={
    'collected_date': '수집일',
    'video_count': '영상 수',
    'total_views': '총 조회수',
    'total_likes': '총 좋아요',
    'total_comments': '총 댓글',
    'views_diff': '조회수 증감',
    'likes_diff': '좋아요 증감'
})

# 증감 컬럼 포맷팅
st.dataframe(
    display_table[['수집일', '영상 수', '총 조회수', '조회수 증감', '총 좋아요', '좋아요 증감', '총 댓글']],
    use_container_width=True,
    column_config={
        "총 조회수": st.column_config.NumberColumn(format="%d"),
        "총 좋아요": st.column_config.NumberColumn(format="%d"),
        "총 댓글": st.column_config.NumberColumn(format="%d"),
        "조회수 증감": st.column_config.NumberColumn(format="%+d"),
        "좋아요 증감": st.column_config.NumberColumn(format="%+d"),
    },
    hide_index=True
)

st.markdown("---")

# --- 3. 통계 추이 차트 (Gapless) ---
st.subheader("📈 관심지표 추이 분석")

tab_views, tab_likes, tab_comments = st.tabs(["👁️ 조회수 트렌드", "❤️ 좋아요 트렌드", "💬 댓글 트렌드"])

def create_trend_chart(df, y_col, diff_col, title, color):
    fig = go.Figure()
    
    # 1) 전체 누적 (Line)
    fig.add_trace(go.Scatter(
        x=df['date_str'], y=df[y_col],
        mode='lines+markers', name='누적 합계',
        line=dict(color=color, width=3),
        marker=dict(size=8)
    ))
    
    # 2) 일일 증가량 (Bar) - 보조축
    fig.add_trace(go.Bar(
        x=df['date_str'], y=df[diff_col],
        name='일일 증가량',
        marker_color=color, opacity=0.3,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(type='category', title='수집 날짜'), # Gapless 설정
        yaxis=dict(title='누적 합계'),
        yaxis2=dict(title='일일 증가량', overlaying='y', side='right', showgrid=False),
        hovermode='x unified',
        height=500
    )
    return fig

with tab_views:
    st.plotly_chart(create_trend_chart(daily_summary, 'total_views', 'views_diff', '조회수 누적 및 증가 추이', '#636EFA'), use_container_width=True)

with tab_likes:
    st.plotly_chart(create_trend_chart(daily_summary, 'total_likes', 'likes_diff', '좋아요 누적 및 증가 추이', '#EF553B'), use_container_width=True)

with tab_comments:
    st.plotly_chart(create_trend_chart(daily_summary, 'total_comments', 'comments_diff', '댓글 수 누적 및 증가 추이', '#00CC96'), use_container_width=True)

# --- 4. 증감률 비교 ---
st.markdown("---")
st.subheader("🚀 관심도 가속도 (증감률)")

fig_rate = go.Figure()
fig_rate.add_trace(go.Bar(
    x=daily_summary['date_str'], y=daily_summary['views_rate'],
    name='조회수 증감률 (%)', marker_color='#636EFA'
))
fig_rate.add_trace(go.Bar(
    x=daily_summary['date_str'], y=daily_summary['likes_rate'],
    name='좋아요 증감률 (%)', marker_color='#EF553B'
))

fig_rate.update_layout(
    title="전일 대비 관심지표 증감률 (%) 비교",
    xaxis=dict(type='category', title='수집 날짜'),
    yaxis_title="증감률 (%)",
    barmode='group',
    height=400,
    legend_title_text="지표"
)
st.plotly_chart(fig_rate, use_container_width=True)
