import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="임성근 전체 요약", page_icon="1️⃣", layout="wide")

# 환경 변수 로드
load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_im_data():
    """임성근 데이터 로드"""
    client = get_supabase_client()
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        response = client.table("im_sung_gen_youtube_comments")\
            .select("*")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        batch_data = response.data
        if not batch_data:
            break
            
        all_data.extend(batch_data)
        if len(batch_data) < page_size:
            break
        offset += page_size
        
    df = pd.DataFrame(all_data)
    
    if not df.empty:
        df['published_at'] = pd.to_datetime(df['published_at'])
        df = df.sort_values('published_at', ascending=False)
        df = df.drop_duplicates(subset=['comment_id'], keep='first')
        
        # 감정 그룹화 (0,2:긍정, 1,3,4:부정, 5:그외)
        def group_sentiment(val):
            if val in [0, 2]: return "긍정"
            if val in [1, 3, 4]: return "부정"
            if val == 5: return "그외"
            return "미분류"

        df['sentiment_group'] = df['llm_sentiment'].apply(group_sentiment)
        
        # 상세 라벨
        label_map = {0: "지지", 1: "분노", 2: "중립", 3: "실망", 4: "조롱", 5: "그외"}
        df['llm_label'] = df['llm_sentiment'].map(label_map)
        
        # 시기 구분 (1월 19일 기준)
        controversy_date = pd.Timestamp("2026-01-19").tz_localize('UTC')
        if df['published_at'].dt.tz is None:
            df['published_at'] = df['published_at'].dt.tz_localize('UTC')
            
        df['period'] = df['published_at'].apply(lambda x: "논란 후" if x >= controversy_date else "논란 전")
        
    return df

# 데이터 로드
df = load_im_data()

if df.empty:
    st.error("임성근 데이터가 없습니다. 먼저 수집 및 분석을 진행해주세요.")
    st.stop()

# --- 헤더 ---
st.title("1️⃣ 임성근 여론 분석 - 전체 요약")
st.markdown(f"**총 댓글 수:** `{len(df):,}` | **분석 완료:** `{df['llm_sentiment'].notnull().sum():,}`")

st.markdown("---")

# --- 핵심 메트릭 ---
st.subheader("📊 핵심 지표")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pos_pct = (df['sentiment_group'] == "긍정").mean() * 100
    st.metric("전체 긍정 비율", f"{pos_pct:.1f}%", delta=f"{pos_pct-20:.1f}%p")

with col2:
    neg_pct = (df['sentiment_group'] == "부정").mean() * 100
    delta_color = "inverse" if neg_pct > 50 else "normal"
    st.metric("전체 부정 비율", f"{neg_pct:.1f}%", delta="High Risk" if neg_pct > 50 else "Normal", delta_color=delta_color)

with col3:
    after_neg = (df[df['period']=='논란 후']['sentiment_group']=='부정').mean() * 100
    st.metric("논란 후 부정 비율", f"{after_neg:.1f}%")

with col4:
    severity_score = after_neg / 10 # 전체 부정 비율보다 논란 후 부정 비율로 심각도 계산
    st.metric("심각도 점수", f"{severity_score:.1f}/10", delta="매우 심각" if severity_score > 7 else "보통")

st.markdown("---")

# --- 감성 분포 및 시기별 비교 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 전체 감성 그룹 분포")
    group_counts = df['sentiment_group'].value_counts().reset_index()
    group_counts.columns = ['Group', 'Count']
    fig_pie = px.pie(
        group_counts, 
        values='Count', 
        names='Group',
        color='Group', 
        color_discrete_map={"긍정": "#00CC96", "부정": "#EF553B", "그외": "#AB63FA"},
        hole=0.4,
        labels={'Group': '감정 그룹', 'Count': '댓글 수'}
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, width="stretch")

with col_right:
    st.subheader("📅 논란 전/후 여론 비교 (1월 19일 기준)")
    period_df = df.groupby(['period', 'sentiment_group']).size().reset_index(name='count')
    period_totals = period_df.groupby('period')['count'].transform('sum')
    period_df['percentage'] = (period_df['count'] / period_totals) * 100
    
    fig_comp = px.bar(
        period_df, 
        x='period', 
        y='percentage', 
        color='sentiment_group',
        barmode='group', 
        text_auto='.1f',
        color_discrete_map={"긍정": "#00CC96", "부정": "#EF553B", "그외": "#AB63FA"},
        category_orders={"period": ["논란 전", "논란 후"]},
        labels={'period': '시기', 'percentage': '비율 (%)', 'sentiment_group': '감정 그룹'}
    )
    fig_comp.update_traces(textposition='outside', cliponaxis=False)
    fig_comp.update_layout(yaxis_title="비율 (%)", height=400, yaxis_range=[0, period_df['percentage'].max() * 1.15])
    st.plotly_chart(fig_comp, width="stretch")

st.markdown("---")

# --- 6가지 감정 상세 분포 (논란 전 vs 후 비교) ---
st.subheader("🎭 논란 전/후 6가지 감정 변화 비교")

# 시기별/감정별 집계
sentiment_comp = df.groupby(['period', 'llm_label']).size().reset_index(name='count')

# 시기별 총합 계산 (비율 산출용)
period_sums = sentiment_comp.groupby('period')['count'].transform('sum')
sentiment_comp['percentage'] = (sentiment_comp['count'] / period_sums * 100).round(1)

# 감정별 색상 맵 (논리적 색상 배치)
emotion_color_map = {
    "지지": "#00CC96",      # 초록 (긍정)
    "분노": "#EF553B",      # 빨강 (강한 부정)
    "중립": "#636EFA",      # 파랑 (중립)
    "실망": "#FFA15A",      # 주황 (부정)
    "조롱": "#AB63FA",      # 보라 (부정)
    "그외": "#B6E880"       # 연두 (기타)
}

# Grouped Bar Chart
fig_bar = px.bar(
    sentiment_comp,
    x='llm_label',
    y='percentage',
    color='period',
    barmode='group',
    text='percentage',
    labels={'llm_label': '감정', 'percentage': '비율 (%)', 'period': '시기'},
    category_orders={"period": ["논란 전", "논란 후"]}  # 순서 고정
)

fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
fig_bar.update_layout(height=450, yaxis_title="비율 (%)", yaxis_range=[0, sentiment_comp['percentage'].max() * 1.15])
st.plotly_chart(fig_bar, width="stretch")

st.markdown("---")

# --- 워드클라우드 ---
st.subheader("☁️ 감정 그룹별 핵심 키워드")
wc_target = st.selectbox("워드클라우드 대상 그룹 선택", ["전체", "긍정", "부정", "그외"])

if wc_target == "전체":
    wc_df = df
else:
    wc_df = df[df['sentiment_group'] == wc_target]

all_kws = []
for k in wc_df['keywords'].dropna():
    all_kws.extend(k)

filtered_kws = [word for word in all_kws if len(word) > 1]

if filtered_kws:
    font_paths = [
        '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
        '/Library/Fonts/NanumGothic.ttf',
        'C:/Windows/Fonts/malgun.ttf'
    ]
    selected_font = next((fp for fp in font_paths if os.path.exists(fp)), None)
    
    wc_color = "Greens" if wc_target == "긍정" else "Reds" if wc_target == "부정" else "Purples"
    wc = WordCloud(
        font_path=selected_font,
        width=1200,
        height=400,
        background_color='white',
        colormap=wc_color
    ).generate(" ".join(filtered_kws))
    
    st.image(wc.to_image(), width="stretch")
    
    # 키워드 Top 10
    st.caption(f"📌 {wc_target} 댓글의 주요 키워드 TOP 10")
    top_10 = Counter(filtered_kws).most_common(10)
    t10_df = pd.DataFrame(top_10, columns=['단어', '빈도'])
    fig_t10 = px.bar(
        t10_df,
        x='빈도',
        y='단어',
        orientation='h',
        color='빈도',
        color_continuous_scale=wc_color
    )
    fig_t10.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
    st.plotly_chart(fig_t10, width="stretch")
else:
    st.info("해당 그룹에 추출된 키워드가 없습니다.")

st.markdown("---")

# --- 데이터 기반 인사이트 ---
st.subheader("💡 핵심 인사이트")

# 계산
before_df = df[df['period'] == '논란 전']
after_df = df[df['period'] == '논란 후']

before_neg = (before_df['sentiment_group'] == '부정').mean() * 100 if not before_df.empty else 0
after_neg = (after_df['sentiment_group'] == '부정').mean() * 100 if not after_df.empty else 0
neg_increase = after_neg - before_neg

# 가장 많은 감정
top_emotion_after = after_df['llm_label'].value_counts().index[0] if not after_df.empty else "N/A"
top_emotion_pct = (after_df['llm_label'].value_counts().iloc[0] / len(after_df) * 100) if not after_df.empty else 0

# 평균 좋아요 (감정별)
if 'likes' in df.columns:
    avg_likes_by_sentiment = df.groupby('llm_label')['likes'].mean().sort_values(ascending=False)
    most_liked_emotion = avg_likes_by_sentiment.index[0]
    most_liked_avg = avg_likes_by_sentiment.iloc[0]
else:
    most_liked_emotion = "N/A"
    most_liked_avg = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    ### 📊 여론 변화

    - **논란 전 부정 비율**: {before_neg:.1f}%
    - **논란 후 부정 비율**: {after_neg:.1f}%
    - **증가폭**: **{neg_increase:+.1f}%p**

    {'🔴 **심각한 악화**' if neg_increase > 30 else '🟡 **중간 정도 악화**' if neg_increase > 15 else '🟢 **경미한 변화**'}

    논란 이후 부정 여론이 급격히 증가했으며,
    {'현재 위기 상황입니다.' if after_neg > 70 else '부정적 여론이 우세합니다.' if after_neg > 50 else '여론이 양분되어 있습니다.'}
    """)

with col2:
    st.markdown(f"""
    ### 🎭 감정 분석

    - **주요 감정 (논란 후)**: **{top_emotion_after}** ({top_emotion_pct:.1f}%)
    - **전체 부정 비율**: {neg_pct:.1f}%
    - **전체 긍정 비율**: {pos_pct:.1f}%

    {
    '😡 분노(분노)가 지배적이며 강한 비난 여론' if top_emotion_after == '분노'
    else '😔 실망(실망)이 주를 이루며 신뢰 하락' if top_emotion_after == '실망'
    else '😏 비꼬는(조롱) 댓글이 많아 조롱 분위기' if top_emotion_after == '조롱'
    else '👍 지지(지지) 여론이 우세' if top_emotion_after == '지지'
    else '중립(중립) 의견이 다수'
    }
    """)

with col3:
    st.markdown(f"""
    ### ⭐ 대중 공감도

    - **가장 공감받는 감정**: **{most_liked_emotion}**
    - **평균 좋아요**: {most_liked_avg:.1f}개

    {
    '분노 댓글이 높은 공감을 받고 있어 대중의 강한 부정 감정을 나타냅니다.' if most_liked_emotion == '분노'
    else '실망 댓글이 공감을 받고 있어 신뢰가 크게 하락했습니다.' if most_liked_emotion == '실망'
    else '비꼬는 댓글이 공감을 받고 있어 조롱이 주류입니다.' if most_liked_emotion == '조롱'
    else '지지 댓글이 공감을 받고 있어 긍정적 지지층이 있습니다.' if most_liked_emotion == '지지'
    else '중립적 의견이 공감을 받고 있습니다.'
    }
    """)

st.markdown("---")

# --- 상세 데이터 ---
st.subheader("💬 분석 상세 데이터")
with st.expander("데이터 보기/숨기기"):
    display_df = df[['published_at', 'author', 'content', 'sentiment_group', 'llm_label', 'likes']].sort_values('published_at', ascending=False)
    st.dataframe(display_df, width="stretch")

st.caption("Opinion Analysis Project | Powered by DeepSeek LLM")
