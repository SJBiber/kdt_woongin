import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import timedelta

# 페이지 설정
st.set_page_config(page_title="추이 비교분석", page_icon="3️⃣", layout="wide")

# 환경 변수 로드
load_dotenv()

# 논란 기준일
CONTROVERSY_DATE = "2026-01-19"

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_trend_data():
    """시계열 데이터 로드"""
    client = get_supabase_client()
    
    # 헬퍼 함수: 데이터 로드 (분석에 필요한 최소 컬럼 + 길이 계산용 content + likes)
    def fetch_all(table):
        data = []
        offset = 0
        limit = 500  # 서버 부하 방지
        while True:
            res = client.table(table)\
                .select("published_at, llm_sentiment, comment_id, content, likes")\
                .range(offset, offset + limit - 1).execute()
            if not res.data: break
            data.extend(res.data)
            if len(res.data) < limit: break
            offset += limit
        return pd.DataFrame(data)

    df_im = fetch_all("im_sung_gen_youtube_comments")
    df_baek = fetch_all("baek_jongwon_youtube_comments")
    
    # 전처리 함수
    def preprocess(df, name):
        if df.empty: return df
        df['published_at'] = pd.to_datetime(df['published_at'])
        # 날짜 정규화
        if df['published_at'].dt.tz is not None:
             df['date'] = df['published_at'].dt.tz_localize(None).dt.normalize()
        else:
             df['date'] = df['published_at'].dt.normalize()
            
        df['sentiment_group'] = df['llm_sentiment'].apply(lambda x: "부정" if x in [1, 3, 4] else "긍정" if x in [0, 2] else "그외")
        df['is_negative'] = (df['sentiment_group'] == '부정').astype(int)
        df['target'] = name
        # 댓글 길이 계산
        df['content_length'] = df['content'].fillna('').str.len()
        
        # 상세 라벨
        label_map = {0: "지지", 1: "분노", 2: "중립", 3: "실망", 4: "조롱", 5: "그외"}
        df['llm_label'] = df['llm_sentiment'].map(label_map)
        
        return df

    df_im = preprocess(df_im, "임성근")
    df_baek = preprocess(df_baek, "백종원")
    
    return df_im, df_baek

df_im, df_baek = load_trend_data()

# --- 헤더 ---
st.title("3️⃣ 추이 비교분석 (시계열 집중)")
st.markdown("""
### 사건 흐름에 따른 데이터 심층 분석
임성근과 백종원의 사례를 각기 다른 시간 단위(일별/월별)로 분석하고, 
댓글의 정성적 특징(길이)이 감정에 따라 어떻게 변하는지 확인합니다.
""")
st.markdown("---")

# 색상 맵 정의
emotion_colors = {
    "지지": "#00CC96", "분노": "#EF553B", "중립": "#636EFA",
    "실망": "#FFA15A", "조롱": "#AB63FA", "그외": "#B6E880"
}

# -------------------------------------------------------------
# 1. 임성근: 논란 전후 1주일 (일별 부정 비율)
# -------------------------------------------------------------
st.subheader("🔴 임성근: 논란 발생 전후 1주일 추이")
st.markdown("> **2026-01-19 전후 1주일(1/12 ~ 1/26)** 기간 동안의 일별 부정 여론 변화입니다.")

# 기간 필터링
controversy_date = pd.Timestamp("2026-01-19")
start_date = controversy_date - timedelta(days=7)
end_date = controversy_date + timedelta(days=8)

mask_im_weekly = (df_im['date'] >= start_date) & (df_im['date'] <= end_date)
df_im_weekly = df_im[mask_im_weekly]

if not df_im_weekly.empty:
    daily_im = df_im_weekly.groupby('date').agg(
        neg_ratio=('is_negative', 'mean')
    ).reset_index()
    daily_im['neg_ratio'] *= 100
    
    fig_im = px.line(
        daily_im, x='date', y='neg_ratio',
        markers=True,
        title='임성근 논란 전후 부정 여론 비율 (%)',
        labels={'date': '날짜', 'neg_ratio': '부정 비율 (%)'}
    )
    # 논란 기준선 추가 (add_vline 대신 add_shape로 우회)
    fig_im.add_shape(
        type="line", x0="2026-01-19", x1="2026-01-19", y0=0, y1=1, yref="paper",
        line=dict(color="red", width=2, dash="dash")
    )
    fig_im.add_annotation(
        x="2026-01-19", y=1, yref="paper",
        text="논란 일자", showarrow=False, textangle=-90, xanchor="left",
        font=dict(color="red")
    )
    fig_im.update_traces(
        line_color='#EF553B', 
        line_width=3,
        text=daily_im['neg_ratio'].round(1).astype(str) + "%", # 라벨 텍스트 수동 지정
        textposition='top center',
        mode='lines+markers+text' # 텍스트 모드 추가
    )
    fig_im.update_layout(yaxis_range=[0, 100], height=400)
    st.plotly_chart(fig_im, use_container_width=True)
else:
    st.info("해당 기간의 임성근 데이터가 부족합니다.")

st.markdown("---")

# -------------------------------------------------------------
# 2. 백종원: 논란 이후 현재까지 (월별 부정 비율)
# -------------------------------------------------------------
st.subheader("🔵 백종원: 장기 월별 여론 패턴")
st.markdown("> 논란 발생 이후 현재까지 여론이 월별로 어떻게 안착해왔는지 보여줍니다.")

if not df_baek.empty:
    # 월별 그룹화를 위해 month 컬럼 생성
    df_baek['month'] = df_baek['published_at'].dt.strftime('%Y-%m')
    
    monthly_baek = df_baek.groupby('month').agg(
        neg_ratio=('is_negative', 'mean')
    ).reset_index().sort_values('month')
    monthly_baek['neg_ratio'] *= 100
    
    fig_baek = px.line(
        monthly_baek, x='month', y='neg_ratio',
        markers=True,
        title='백종원 월별 부정 여론 비율 (%)',
        labels={'month': '월', 'neg_ratio': '부정 비율 (%)'}
    )
    fig_baek.update_traces(
        line_color='#636EFA', 
        line_width=3,
        mode='lines+markers+text',
        text=monthly_baek['neg_ratio'].round(1).astype(str) + "%",
        textposition='top center'
    )
    fig_baek.update_layout(yaxis_range=[0, 100], height=400)
    st.plotly_chart(fig_baek, use_container_width=True)
else:
    st.info("백종원 데이터가 없습니다.")

st.markdown("---")

st.markdown("---")

# -------------------------------------------------------------
# 4. 임성근: 논란 전/후 댓글 좋아요(공감) 수 비교
# -------------------------------------------------------------
st.subheader("👍 임성근: 논란 전/후 댓글 공감(좋아요) 수 비교")
st.markdown("> 호감 여론일 때와 비난 여론일 때, 사람들이 댓글에 좋아요를 누르는 패턴이 다를까요?")

if not df_im.empty and 'likes' in df_im.columns:
    # 논란 기준일로 전/후 분리
    controversy_date = pd.Timestamp("2026-01-19")
    df_im_before = df_im[df_im['date'] < controversy_date]
    df_im_after = df_im[df_im['date'] >= controversy_date]

    # 좋아요 통계 계산
    likes_stats = pd.DataFrame({
        '시기': ['논란 전 (호감 여론)', '논란 후 (비난 여론)'],
        '총 좋아요 수': [
            df_im_before['likes'].sum() if not df_im_before.empty else 0,
            df_im_after['likes'].sum() if not df_im_after.empty else 0
        ],
        '평균 좋아요 수': [
            df_im_before['likes'].mean() if not df_im_before.empty else 0,
            df_im_after['likes'].mean() if not df_im_after.empty else 0
        ],
        '댓글 수': [
            len(df_im_before),
            len(df_im_after)
        ]
    })

    # 2개의 컬럼으로 차트 배치
    col1, col2 = st.columns(2)

    with col1:
        # 총 좋아요 수 비교
        fig_total_likes = px.bar(
            likes_stats, x='시기', y='총 좋아요 수',
            color='시기',
            color_discrete_map={
                '논란 전 (호감 여론)': '#00CC96',
                '논란 후 (비난 여론)': '#EF553B'
            },
            text=likes_stats['총 좋아요 수'].apply(lambda x: f'{x:,.0f}'),
            title='총 좋아요 수 비교'
        )
        fig_total_likes.update_traces(textposition='outside', cliponaxis=False)
        fig_total_likes.update_layout(showlegend=False, height=400, yaxis_range=[0, likes_stats['총 좋아요 수'].max() * 1.15])
        st.plotly_chart(fig_total_likes, use_container_width=True)

    with col2:
        # 평균 좋아요 수 비교
        fig_avg_likes = px.bar(
            likes_stats, x='시기', y='평균 좋아요 수',
            color='시기',
            color_discrete_map={
                '논란 전 (호감 여론)': '#00CC96',
                '논란 후 (비난 여론)': '#EF553B'
            },
            text=likes_stats['평균 좋아요 수'].apply(lambda x: f'{x:.1f}'),
            title='댓글당 평균 좋아요 수 비교'
        )
        fig_avg_likes.update_traces(textposition='outside', cliponaxis=False)
        fig_avg_likes.update_layout(showlegend=False, height=400, yaxis_range=[0, likes_stats['평균 좋아요 수'].max() * 1.15])
        st.plotly_chart(fig_avg_likes, use_container_width=True)

    # 상세 통계 테이블
    st.dataframe(
        likes_stats.style.format({
            '총 좋아요 수': '{:,.0f}',
            '평균 좋아요 수': '{:.2f}',
            '댓글 수': '{:,}'
        }),
        use_container_width=True
    )

    st.markdown("""
    > **인사이트**:
    > - **호감 여론** 시기에는 팬들이 긍정적인 댓글에 좋아요를 누르는 경향이 있습니다.
    > - **비난 여론** 시기에는 비판적인 댓글에 더 많은 공감이 모이는 경향을 볼 수 있습니다.
    > - 평균 좋아요 수를 비교하면 어떤 시기에 댓글 참여도가 높았는지 파악할 수 있습니다.
    """)
else:
    st.info("임성근 좋아요 데이터가 없어 비교할 수 없습니다.")

st.markdown("---")

# -------------------------------------------------------------
# 5. 임성근: 논란 전/후 영상 공감 지수 비교
# -------------------------------------------------------------
st.subheader("🎬 임성근: 논란 전/후 영상 공감 지수 비교")
st.markdown("> 영상 조회수 대비 좋아요 비율로 시청자들의 긍정적 반응 정도를 측정합니다.")
st.markdown("> **영상 공감 지수 = 좋아요수 / 조회수 × 100**")

@st.cache_data(ttl=300)
def load_video_stats():
    """영상 통계 데이터 로드"""
    client = get_supabase_client()
    try:
        res = client.table("im_sung_gen_video_stats")\
            .select("*")\
            .execute()
        if res.data:
            return pd.DataFrame(res.data)
    except Exception as e:
        st.warning(f"영상 통계 데이터 로드 실패: {e}")
    return pd.DataFrame()

df_video_stats = load_video_stats()

if not df_video_stats.empty:
    # 2022년도 데이터 제외 (2023년 이후 데이터만 사용)
    df_video_stats['upload_date'] = pd.to_datetime(df_video_stats['upload_date'])
    df_video_stats = df_video_stats[df_video_stats['upload_date'] >= "2023-01-01"]
    
    # 논란 전/후 분리
    df_video_before = df_video_stats[df_video_stats['is_before_controversy'] == True]
    df_video_after = df_video_stats[df_video_stats['is_before_controversy'] == False]

    # 통계 계산
    def calc_video_stats(df, label):
        if df.empty:
            return {
                '시기': label,
                '영상 수': 0,
                '총 조회수': 0,
                '총 좋아요': 0,
                '전체 공감 지수 (%)': 0,
                '영상별 평균 공감 지수 (%)': 0
            }
        total_views = df['view_count'].sum()
        total_likes = df['like_count'].sum()
        overall_rate = (total_likes / total_views * 100) if total_views > 0 else 0
        avg_rate = df['engagement_rate'].mean() if 'engagement_rate' in df.columns else 0

        return {
            '시기': label,
            '영상 수': len(df),
            '총 조회수': total_views,
            '총 좋아요': total_likes,
            '전체 공감 지수 (%)': overall_rate,
            '영상별 평균 공감 지수 (%)': avg_rate
        }

    stats_before = calc_video_stats(df_video_before, '논란 전 (호감 여론)')
    stats_after = calc_video_stats(df_video_after, '논란 후 (비난 여론)')

    video_stats_df = pd.DataFrame([stats_before, stats_after])

    # 비교 표 출력
    st.markdown("#### 📊 논란 전/후 영상 통계 비교 (좋아요 수/조회수 * 100)")
    st.dataframe(
        video_stats_df.style.format({
            '총 조회수': '{:,.0f}',
            '총 좋아요': '{:,.0f}',
            '전체 공감 지수 (%)': '{:.2f}',
            '영상별 평균 공감 지수 (%)': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    # 바 차트 - Engagement Rate 비교
    col1, col2 = st.columns(2)

    with col1:
        fig_overall = px.bar(
            video_stats_df, x='시기', y='전체 공감 지수 (%)',
            color='시기',
            color_discrete_map={
                '논란 전 (호감 여론)': '#00CC96',
                '논란 후 (비난 여론)': '#EF553B'
            },
            text=video_stats_df['전체 공감 지수 (%)'].apply(lambda x: f'{x:.2f}%'),
            title='전체 영상 공감 지수 비교'
        )
        fig_overall.update_traces(textposition='outside', cliponaxis=False)
        fig_overall.update_layout(showlegend=False, height=400, yaxis_range=[0, video_stats_df['전체 공감 지수 (%)'].max() * 1.15])
        st.plotly_chart(fig_overall, use_container_width=True)

    with col2:
        fig_avg = px.bar(
            video_stats_df, x='시기', y='영상별 평균 공감 지수 (%)',
            color='시기',
            color_discrete_map={
                '논란 전 (호감 여론)': '#00CC96',
                '논란 후 (비난 여론)': '#EF553B'
            },
            text=video_stats_df['영상별 평균 공감 지수 (%)'].apply(lambda x: f'{x:.2f}%'),
            title='영상별 평균 공감 지수 비교'
        )
        fig_avg.update_traces(textposition='outside', cliponaxis=False)
        fig_avg.update_layout(showlegend=False, height=400, yaxis_range=[0, video_stats_df['영상별 평균 공감 지수 (%)'].max() * 1.15])
        st.plotly_chart(fig_avg, use_container_width=True)

    # 개별 영상 목록
    with st.expander("📋 개별 영상 상세 보기"):
        display_cols = ['title', 'channel', 'upload_date', 'view_count', 'like_count', 'engagement_rate', 'is_before_controversy']
        available_cols = [c for c in display_cols if c in df_video_stats.columns]

        df_display = df_video_stats[available_cols].copy()
        df_display['시기'] = df_display['is_before_controversy'].apply(
            lambda x: '🟢 논란 전' if x == True else '🔴 논란 후' if x == False else '⚪ 미상'
        )
        df_display = df_display.drop(columns=['is_before_controversy'], errors='ignore')
        df_display = df_display.rename(columns={
            'title': '제목', 'channel': '채널', 'upload_date': '업로드일',
            'view_count': '조회수', 'like_count': '좋아요', 'engagement_rate': '영상 공감 지수(%)'
        })

        st.dataframe(
            df_display.style.format({
                '조회수': '{:,.0f}',
                '좋아요': '{:,.0f}',
                '영상 공감 지수(%)': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("""
    > **인사이트**:
    > - **영상 공감 지수(%)**는 조회수 대비 좋아요 비율로, 시청자들의 적극적인 호감 표현 정도를 나타냅니다.
    > - 논란 전에는 팬들이 적극적으로 좋아요를 눌러 비율이 높고, 논란 후에는 비율이 낮아지는 경향이 있습니다.
    """)

    st.markdown("---")

    # -------------------------------------------------------------
    # 5-1. 표준편차 비교 그래프
    # -------------------------------------------------------------
    st.markdown("#### 📉 논란 전/후 영상 공감 지수 표준편차 비교")
    st.markdown("> 표준편차가 클수록 영상별 반응 편차가 크고, 작을수록 일관된 반응을 보입니다.")

    # 표준편차 계산
    std_before = df_video_before['engagement_rate'].std() if not df_video_before.empty and len(df_video_before) > 1 else 0
    std_after = df_video_after['engagement_rate'].std() if not df_video_after.empty and len(df_video_after) > 1 else 0
    mean_before = df_video_before['engagement_rate'].mean() if not df_video_before.empty else 0
    mean_after = df_video_after['engagement_rate'].mean() if not df_video_after.empty else 0

    std_stats_df = pd.DataFrame({
        '시기': ['논란 전 (호감 여론)', '논란 후 (비난 여론)'],
        '평균 (%)': [mean_before, mean_after],
        '표준편차 (%)': [std_before, std_after]
    })

    col1, col2 = st.columns(2)

    with col1:
        # 평균 ± 표준편차 바 차트
        fig_std = go.Figure()
        fig_std.add_trace(go.Bar(
            x=['논란 전', '논란 후'],
            y=[mean_before, mean_after],
            error_y=dict(type='data', array=[std_before, std_after], visible=True),
            marker_color=['#00CC96', '#EF553B'],
            text=[f'{mean_before:.2f}%', f'{mean_after:.2f}%'],
            textposition='outside'
        ))
        fig_std.update_layout(
            title='평균 영상 공감 지수 (± 표준편차)',
            yaxis_title='영상 공감 지수 (%)',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_std, use_container_width=True)

    with col2:
        # 표준편차 비교
        fig_std_only = px.bar(
            std_stats_df, x='시기', y='표준편차 (%)',
            color='시기',
            color_discrete_map={
                '논란 전 (호감 여론)': '#00CC96',
                '논란 후 (비난 여론)': '#EF553B'
            },
            text=std_stats_df['표준편차 (%)'].apply(lambda x: f'{x:.2f}%'),
            title='표준편차 비교'
        )
        fig_std_only.update_traces(textposition='outside', cliponaxis=False)
        fig_std_only.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_std_only, use_container_width=True)

    # 통계 테이블
    st.dataframe(
        std_stats_df.style.format({
            '평균 (%)': '{:.2f}',
            '표준편차 (%)': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # -------------------------------------------------------------
    # 5-2. 날짜별 시계열 그래프
    # -------------------------------------------------------------
    st.markdown("#### 📈 업로드 날짜별 영상 공감 지수 추이")
    st.markdown("> 같은 날짜에 여러 영상이 있으면 평균값으로 표시합니다.")

    # 날짜 데이터 전처리
    df_timeline = df_video_stats.copy()
    df_timeline = df_timeline[df_timeline['upload_date'].notna()]

    if not df_timeline.empty:
        df_timeline['upload_date'] = pd.to_datetime(df_timeline['upload_date'])

        # 날짜별 평균 계산
        daily_engagement = df_timeline.groupby('upload_date').agg(
            avg_engagement=('engagement_rate', 'mean'),
            video_count=('video_id', 'count')
        ).reset_index()
        daily_engagement = daily_engagement.sort_values('upload_date')

        # 논란 기준일
        controversy_ts = pd.Timestamp(CONTROVERSY_DATE)

        # 날짜를 문자열로 변환 (빈 날짜 제거용)
        daily_engagement['date_str'] = daily_engagement['upload_date'].dt.strftime('%Y-%m-%d')

        fig_timeline = px.line(
            daily_engagement, x='date_str', y='avg_engagement',
            markers=True,
            title='업로드 날짜별 평균 영상 공감 지수 추이',
            labels={'date_str': '업로드 날짜', 'avg_engagement': '영상 공감 지수 (%)'}
        )

        # 논란 기준선 추가 (우회)
        fig_timeline.add_shape(
            type="line", x0="2026-01-19", x1="2026-01-19", y0=0, y1=1, yref="paper",
            line=dict(color="red", width=2, dash="dash")
        )
        fig_timeline.add_annotation(
            x="2026-01-19", y=1.05, yref="paper",
            text="논란 발생일 (01/19)", showarrow=False, textangle=-90, xanchor="left",
            font=dict(color="red")
        )

        # 논란 전/후 평균 수평선 추가
        if mean_before > 0:
            fig_timeline.add_hline(
                y=mean_before, line_dash="dot", line_color="#00CC96",
                annotation_text=f"논란 전 평균: {mean_before:.2f}%",
                annotation_position="top left"
            )
        if mean_after > 0:
            fig_timeline.add_hline(
                y=mean_after, line_dash="dot", line_color="#EF553B",
                annotation_text=f"논란 후 평균: {mean_after:.2f}%",
                annotation_position="bottom left"
            )

        # 데이터 포인트에 영상 수 표시
        fig_timeline.update_traces(
            line_color='#636EFA',
            line_width=2,
            mode='lines+markers+text',
            text=daily_engagement['avg_engagement'].round(2).astype(str) + '%',
            textposition='top center'
        )

        fig_timeline.update_layout(
            height=450,
            xaxis={'type': 'category'},
            yaxis_range=[0, daily_engagement['avg_engagement'].max() * 1.2]
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        # 날짜별 상세 테이블
        with st.expander("📋 날짜별 상세 데이터"):
            daily_engagement_display = daily_engagement.copy()
            daily_engagement_display['upload_date'] = daily_engagement_display['upload_date'].dt.strftime('%Y-%m-%d')
            daily_engagement_display = daily_engagement_display.rename(columns={
                'upload_date': '업로드 날짜',
                'avg_engagement': '평균 영상 공감 지수 (%)',
                'video_count': '영상 수'
            })
            st.dataframe(
                daily_engagement_display.style.format({
                    '평균 영상 공감 지수 (%)': '{:.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("""
        > **인사이트**:
        > - 논란 발생일(2026-01-19) 전후로 영상 공감 지수 변화 추이를 확인할 수 있습니다.
        > - 표준편차가 작으면 시청자 반응이 일관적이고, 크면 영상별로 반응 편차가 큽니다.
        """)

        st.markdown("---")

        # -------------------------------------------------------------
        # 5-3. 조회수 및 좋아요 수 시계열 (이중축)
        # -------------------------------------------------------------
        st.markdown("#### 👁️ 업로드 날짜별 조회수 및 좋아요 추이 (이중축)")
        st.info("💡 동일한 날짜에 여러 영상이 업로드된 경우 **총합**으로 계산되었습니다.")

        # 날짜별 조회수/좋아요 총합 계산
        daily_stats = df_timeline.groupby('upload_date').agg(
            total_views=('view_count', 'sum'),
            total_likes=('like_count', 'sum')
        ).reset_index().sort_values('upload_date')
        
        # 날짜를 문자열로 변환 (빈 날짜 제거용)
        daily_stats['date_str'] = daily_stats['upload_date'].dt.strftime('%Y-%m-%d')

        # 이중축 그래프 생성
        fig_dual = go.Figure()

        # 조회수 (Bar - 왼쪽 Y축)
        fig_dual.add_trace(go.Bar(
            x=daily_stats['date_str'],
            y=daily_stats['total_views'],
            name='총 조회수',
            marker_color='#636EFA',
            offsetgroup=1,
            yaxis='y'
        ))

        # 좋아요 (Bar - 오른쪽 Y축)
        fig_dual.add_trace(go.Bar(
            x=daily_stats['date_str'],
            y=daily_stats['total_likes'],
            name='총 좋아요 수',
            marker_color='#EF553B',
            offsetgroup=2,
            yaxis='y2'
        ))

        # 레이아웃 설정 (더 안전한 구문 사용)
        fig_dual.update_layout(
            title={'text': '업로드 날짜별 총 조회수 및 좋아요 추이'},
            xaxis={'title': {'text': '업로드 날짜'}, 'type': 'category'},
            yaxis={
                'title': {'text': '총 조회수', 'font': {'color': '#636EFA'}},
                'tickfont': {'color': '#636EFA'}
            },
            yaxis2={
                'title': {'text': '총 좋아요 수', 'font': {'color': '#EF553B'}},
                'tickfont': {'color': '#EF553B'},
                'overlaying': 'y',
                'side': 'right',
                'showgrid': False
            },
            legend={'x': 0.01, 'y': 0.99, 'bgcolor': 'rgba(255,255,255,0.5)'},
            hovermode='x unified',
            bargap=0.15,  # 막대 그룹 간 거리 좁힘
            height=500
        )

        # 논란 기준선 추가 (우회)
        fig_dual.add_shape(
            type="line", x0="2026-01-19", x1="2026-01-19", y0=0, y1=1, yref="paper",
            line=dict(color="red", width=2, dash="dash")
        )
        fig_dual.add_annotation(
            x="2026-01-19", y=1.05, yref="paper",
            text="논란 일자", showarrow=False, textangle=-90, xanchor="left",
            font=dict(color="red")
        )

        st.plotly_chart(fig_dual, use_container_width=True)
    else:
        st.info("날짜 데이터가 있는 영상이 없어 시계열 그래프를 표시할 수 없습니다.")

else:
    st.info("영상 통계 데이터가 없습니다. `5_video_stats_collector.py`를 실행하여 데이터를 수집해주세요.")
