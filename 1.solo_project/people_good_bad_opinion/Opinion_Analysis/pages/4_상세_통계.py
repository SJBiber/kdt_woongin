import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="상세 통계", page_icon="4️⃣", layout="wide")

# 환경 변수 로드
load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_detailed_data():
    """상세 통계용 데이터 로드"""
    client = get_supabase_client()
    
    # 임성근 데이터
    im_data = []
    offset = 0
    page_size = 1000
    
    while True:
        response = client.table("im_sung_gen_youtube_comments")\
            .select("*")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        batch = response.data
        if not batch:
            break
        im_data.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    
    # 백종원 데이터
    baek_data = []
    offset = 0
    
    while True:
        response = client.table("baek_jongwon_youtube_comments")\
            .select("*")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        batch = response.data
        if not batch:
            break
        baek_data.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    
    # DataFrame 변환
    df_im = pd.DataFrame(im_data)
    df_baek = pd.DataFrame(baek_data)
    
    # 감정 그룹화 함수
    def group_sentiment(val):
        if val in [0, 2]: return "긍정"
        if val in [1, 3, 4]: return "부정"
        if val == 5: return "그외"
        return "미분류"

    label_map = {0: "지지", 1: "분노", 2: "중립", 3: "실망", 4: "조롱", 5: "그외"}
    SENTIMENT_ORDER = ["지지", "분노", "중립", "실망", "조롱", "그외"]

    # 데이터 전처리
    CONTROVERSY_DATE = pd.Timestamp("2026-01-19")

    if not df_im.empty:
        df_im['published_at'] = pd.to_datetime(df_im['published_at'])
        # 시간대 제거하여 비교 가능하게 함
        df_im['date_only'] = df_im['published_at'].dt.tz_localize(None).dt.normalize()
        df_im = df_im.drop_duplicates(subset=['comment_id'], keep='first')
        df_im['sentiment_group'] = df_im['llm_sentiment'].apply(group_sentiment)
        df_im['llm_label'] = df_im['llm_sentiment'].map(label_map)
        df_im['period'] = df_im['date_only'].apply(lambda x: "논란 후" if x >= CONTROVERSY_DATE else "논란 전")
        df_im['content_length'] = df_im['content'].fillna('').str.len()

    if not df_baek.empty:
        df_baek['published_at'] = pd.to_datetime(df_baek['published_at'])
        df_baek['date_only'] = df_baek['published_at'].dt.tz_localize(None).dt.normalize()
        df_baek = df_baek.drop_duplicates(subset=['comment_id'], keep='first')
        df_baek['sentiment_group'] = df_baek['llm_sentiment'].apply(group_sentiment)
        df_baek['llm_label'] = df_baek['llm_sentiment'].map(label_map)
        # 백종원 논란은 2025년 2월경이었으나 현재 분석 맥락에 맞춰 임성근 기준일 적용 혹은 별도 기준 필요
        # 요청사항이 '논란 전/후'이므로 임성근 기준일로 일단 통일 (혹은 백종원용 별도 기준 필요시 수정 가능)
        df_baek['period'] = df_baek['date_only'].apply(lambda x: "논란 후" if x >= CONTROVERSY_DATE else "논란 전")
        df_baek['content_length'] = df_baek['content'].fillna('').str.len()

    return df_im, df_baek

# 데이터 로드
df_im, df_baek = load_detailed_data()

if df_im.empty:
    st.error("임성근 데이터가 없습니다.")
    st.stop()

# --- 헤더 ---
st.title("4️⃣ 상세 통계 및 데이터 탐색")
st.markdown("### 감정별 상세 분석 및 영향력 분석")

st.markdown("---")

# --- 분석 대상 선택 ---
analysis_target = st.selectbox(
    "분석 대상 선택",
    ["임성근", "백종원"] if not df_baek.empty else ["임성근"]
)

df_selected = df_im if analysis_target == "임성근" else df_baek

st.markdown("---")

# --- 감정별 상세 통계 ---
st.subheader("📊 감정별 상세 통계")

def get_sentiment_stats(df):
    if df.empty:
        return pd.DataFrame()
    stats = df.groupby('llm_label').agg({
        'comment_id': 'count',
        'likes': ['mean', 'sum', 'max'],
        'content_length': 'mean' # 이미 정의된 컬럼 사용
    }).reset_index()
    stats.columns = ['감정', '댓글 수', '평균 좋아요', '총 좋아요', '최대 좋아요', '평균 글자 수']
    stats['비율 (%)'] = (stats['댓글 수'] / stats['댓글 수'].sum() * 100).round(1)
    
    # 순서 고정
    sentiment_order = ["지지", "분노", "중립", "실망", "조롱", "그외"]
    stats['감정'] = pd.Categorical(stats['감정'], categories=sentiment_order, ordered=True)
    return stats.sort_values('감정')

df_before = df_selected[df_selected['period'] == "논란 전"]
df_after = df_selected[df_selected['period'] == "논란 후"]

col_tab1, col_tab2 = st.columns(2)

with col_tab1:
    st.markdown("#### 🕒 논란 전")
    if not df_before.empty:
        stats_before = get_sentiment_stats(df_before)
        st.dataframe(stats_before.style.format({
            '평균 좋아요': '{:.1f}', '총 좋아요': '{:,.0f}', '최대 좋아요': '{:,.0f}',
            '평균 글자 수': '{:.0f}', '비율 (%)': '{:.1f}%'
        }), use_container_width=True)
    else:
        st.info("논란 전 데이터가 없습니다.")

with col_tab2:
    st.markdown("#### 🚨 논란 후")
    if not df_after.empty:
        stats_after = get_sentiment_stats(df_after)
        st.dataframe(stats_after.style.format({
            '평균 좋아요': '{:.1f}', '총 좋아요': '{:,.0f}', '최대 좋아요': '{:,.0f}',
            '평균 글자 수': '{:.0f}', '비율 (%)': '{:.1f}%'
        }), use_container_width=True)
    else:
        st.info("논란 후 데이터가 없습니다.")

st.markdown("---")

# --- 영향력 분석 (좋아요 기반) ---
st.subheader("⭐ 영향력 분석 (좋아요 기반)")

st.markdown("""
좋아요가 많은 댓글은 대중의 공감을 받은 의견으로, 여론의 핵심을 파악하는 데 중요합니다.
""")

# 좋아요 Top 10 댓글
top_liked = df_selected.nlargest(10, 'likes')[['content', 'likes', 'llm_label', 'published_at']]
top_liked['published_at'] = top_liked['published_at'].dt.strftime('%Y-%m-%d')

st.markdown("#### 📌 좋아요 Top 10 댓글")
for idx, row in top_liked.iterrows():
    with st.expander(f"❤️ {row['likes']:,}개 | {row['llm_label']} | {row['published_at']}"):
        st.write(row['content'])

st.markdown("---")

# --- 감정별 좋아요 분포 ---
st.subheader("📈 감정별 좋아요 분포")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🕒 논란 전")
    if not df_before.empty:
        fig_box_before = px.box(
            df_before, x='llm_label', y='likes', color='llm_label',
            labels={'llm_label': '감정', 'likes': '좋아요 수'},
            title='논란 전 감정별 좋아요 분포',
            category_orders={"llm_label": ["지지", "분노", "중립", "실망", "조롱", "그외"]}
        )
        fig_box_before.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_box_before, use_container_width=True)
    else:
        st.info("데이터 없음")

with col2:
    st.markdown("#### 🚨 논란 후")
    if not df_after.empty:
        fig_box_after = px.box(
            df_after, x='llm_label', y='likes', color='llm_label',
            labels={'llm_label': '감정', 'likes': '좋아요 수'},
            title='논란 후 감정별 좋아요 분포',
            category_orders={"llm_label": ["지지", "분노", "중립", "실망", "조롱", "그외"]}
        )
        fig_box_after.update_layout(showlegend=False, height=400)
        # 좋아요 수가 급증한 경우 로그 스케일 적용
        if df_after['likes'].max() > 100:
            fig_box_after.update_layout(yaxis_type="log")
        st.plotly_chart(fig_box_after, use_container_width=True)
    else:
        st.info("데이터 없음")

st.markdown("---")

# --- 댓글 길이 분석 ---
st.subheader("📝 댓글 길이 분석")

df_selected['content_length'] = df_selected['content'].str.len()

col1, col2 = st.columns(2)

st.markdown("#### 📏 감정별 평균 댓글 길이 비교")
col_len1, col_len2 = st.columns(2)

with col_len1:
    st.markdown("#### 🕒 논란 전")
    if not df_before.empty:
        avg_len_before = df_before.groupby('llm_label')['content_length'].mean().reset_index()
        fig_len_before = px.bar(
            avg_len_before, x='llm_label', y='content_length', color='llm_label', 
            title='논란 전 감정별 평균 길이',
            category_orders={"llm_label": ["지지", "분노", "중립", "실망", "조롱", "그외"]}
        )
        fig_len_before.update_traces(textposition='outside', cliponaxis=False)
        fig_len_before.update_layout(showlegend=False, height=350, yaxis_range=[0, avg_len_before['content_length'].max() * 1.15])
        st.plotly_chart(fig_len_before, use_container_width=True)

with col_len2:
    st.markdown("#### 🚨 논란 후")
    if not df_after.empty:
        avg_len_after = df_after.groupby('llm_label')['content_length'].mean().reset_index()
        fig_len_after = px.bar(
            avg_len_after, x='llm_label', y='content_length', color='llm_label', 
            title='논란 후 감정별 평균 길이',
            category_orders={"llm_label": ["지지", "분노", "중립", "실망", "조롱", "그외"]}
        )
        fig_len_after.update_traces(textposition='outside', cliponaxis=False)
        fig_len_after.update_layout(showlegend=False, height=350, yaxis_range=[0, avg_len_after['content_length'].max() * 1.15])
        st.plotly_chart(fig_len_after, use_container_width=True)

st.markdown("#### 📊 전체 글자 수 분포 비교")
col_hist1, col_hist2 = st.columns(2)

with col_hist1:
    if not df_before.empty:
        fig_hist_before = px.histogram(df_before, x='content_length', nbins=30, title='논란 전 길이 분포', color_discrete_sequence=['#636EFA'])
        fig_hist_before.update_layout(height=350)
        st.plotly_chart(fig_hist_before, use_container_width=True)

with col_hist2:
    if not df_after.empty:
        fig_hist_after = px.histogram(df_after, x='content_length', nbins=30, title='논란 후 길이 분포', color_discrete_sequence=['#EF553B'])
        fig_hist_after.update_layout(height=350)
        st.plotly_chart(fig_hist_after, use_container_width=True)

st.markdown("---")

# --- 키워드 네트워크 분석 ---
st.subheader("🔗 주요 키워드 공출현 분석")

# 감정 리스트 (순서 고정)
sentiment_order = ["지지", "분노", "중립", "실망", "조롱", "그외"]
available_sentiments = [s for s in sentiment_order if s in df_selected['llm_label'].unique()]

selected_sentiment = st.selectbox(
    "감정 선택",
    available_sentiments
)

filtered_df = df_selected[df_selected['llm_label'] == selected_sentiment]

all_keywords = []
for k in filtered_df['keywords'].dropna():
    all_keywords.extend(k)

keyword_counts = Counter([w for w in all_keywords if len(w) > 1])
top_keywords = keyword_counts.most_common(20)

if top_keywords:
    keyword_df = pd.DataFrame(top_keywords, columns=['키워드', '빈도'])
    
    fig_keywords = px.bar(
        keyword_df,
        x='빈도',
        y='키워드',
        orientation='h',
        color='빈도',
        color_continuous_scale='Viridis',
        title=f'{selected_sentiment} 감정의 주요 키워드 Top 20'
    )
    fig_keywords.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
    st.plotly_chart(fig_keywords, width="stretch")
else:
    st.info("해당 감정에 키워드가 없습니다.")

st.markdown("---")

# --- 데이터 탐색 및 다운로드 ---
st.subheader("💾 데이터 탐색 및 다운로드")

# 필터링 옵션
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    sentiment_filter = st.multiselect(
        "감정 필터",
        available_sentiments,
        default=available_sentiments
    )

with col_filter2:
    min_likes = st.number_input("최소 좋아요 수", min_value=0, value=0)

with col_filter3:
    min_length = st.number_input("최소 글자 수", min_value=0, value=0)

# 필터 적용
filtered_data = df_selected[
    (df_selected['llm_label'].isin(sentiment_filter)) &
    (df_selected['likes'] >= min_likes) &
    (df_selected['content_length'] >= min_length)
]

st.markdown(f"**필터링된 데이터: {len(filtered_data):,}개**")

# 데이터 표시
with st.expander("데이터 보기"):
    display_cols = ['published_at', 'period', 'content', 'llm_label', 'sentiment_group', 'likes', 'content_length']
    st.dataframe(
        filtered_data[display_cols].sort_values('published_at', ascending=False),
        width="stretch"
    )

# CSV 다운로드
csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 CSV 다운로드",
    data=csv,
    file_name=f"{analysis_target}_sentiment_analysis.csv",
    mime="text/csv"
)

st.markdown("---")

# --- 통계 요약 ---
st.subheader("📊 전체 통계 요약")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("총 댓글 수", f"{len(df_selected):,}")

with col2:
    st.metric("평균 좋아요", f"{df_selected['likes'].mean():.1f}")

with col3:
    st.metric("평균 글자 수", f"{df_selected['content_length'].mean():.0f}")

with col4:
    st.metric("가장 많은 감정", df_selected['llm_label'].mode()[0])

st.caption("Opinion Analysis Project | Powered by DeepSeek LLM")
