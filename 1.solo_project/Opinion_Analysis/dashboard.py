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

# 1. 설정 및 데이터 로드
st.set_page_config(page_title="임성근 유튜브 여론 분석 대시보드", layout="wide")
load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=60)
def load_data():
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
        
        # [신규] 감정 그룹화 함수 (0:긍정, 1,2,3,4:부정, 5:그외)
        def group_sentiment(val):
            if val == 0: return "긍정"
            if val in [1, 2, 3, 4]: return "부정"
            if val == 5: return "그외"
            return "미분류"

        df['sentiment_group'] = df['llm_sentiment'].apply(group_sentiment)
        
        # [복구] 상세 분석용 6종 텍스트 라벨 맵핑
        label_map = {0: "Support", 1: "Anger", 2: "Neutral", 3: "Disappointment", 4: "Sarcasm", 5: "Inquiry"}
        df['llm_label'] = df['llm_sentiment'].map(label_map)
        
        # 시기 구분 (1월 18일 기준)
        controversy_date = pd.Timestamp("2026-01-18").tz_localize('UTC')
        # 데이터에 타임존이 있을 수 있으므로 처리
        if df['published_at'].dt.tz is None:
            df['published_at'] = df['published_at'].dt.tz_localize('UTC')
            
        df['period'] = df['published_at'].apply(lambda x: "논란 후" if x >= controversy_date else "논란 전")
        
    return df

df = load_data()

if df.empty:
    st.error("데이터가 없습니다. 먼저 수집 및 분석을 진행해주세요.")
    st.stop()

# --- 헤더 ---
st.title("👨‍🍳 임성근 유튜브 여론 분석 대시보드")
st.markdown(f"**총 댓글 수:** `{len(df)}` | **분석 완료:** `{df['llm_sentiment'].notnull().sum()}`")

# --- 메트릭 ---
c1, c2, c3 = st.columns(3)
with c1:
    pos_pct = (df['sentiment_group'] == "긍정").mean() * 100
    st.metric("전체 긍정 비율", f"{pos_pct:.1f}%")
with c2:
    neg_pct = (df['sentiment_group'] == "부정").mean() * 100
    st.metric("전체 부정 비율", f"{neg_pct:.1f}%", delta="High Risk" if neg_pct > 50 else None, delta_color="inverse")
with c3:
    st.metric("논란 후 부정 증가율", f"{((df[df['period']=='논란 후']['sentiment_group']=='부정').mean() * 100):.1f}%")

st.divider()

# --- 2 & 3. 감성 분포 및 시기별 비교 ---
col_main_left, col_main_right = st.columns(2)

with col_main_left:
    st.subheader("📊 전체 감성 그룹 분포")
    group_counts = df['sentiment_group'].value_counts().reset_index()
    group_counts.columns = ['Group', 'Count']
    fig_pie = px.pie(group_counts, values='Count', names='Group', 
                     color='Group', color_discrete_map={"긍정": "#00CC96", "부정": "#EF553B", "그외": "#AB63FA"},
                     hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_main_right:
    st.subheader("� 논란 전/후 여론 비교 (1월 19일 기준)")
    period_df = df.groupby(['period', 'sentiment_group']).size().reset_index(name='count')
    # 비율로 변환
    period_totals = period_df.groupby('period')['count'].transform('sum')
    period_df['percentage'] = (period_df['count'] / period_totals) * 100
    
    fig_comp = px.bar(period_df, x='period', y='percentage', color='sentiment_group',
                      barmode='group', text_auto='.1f',
                      color_discrete_map={"긍정": "#00CC96", "부정": "#EF553B", "그외": "#AB63FA"},
                      category_orders={"period": ["논란 전", "논란 후"]})
    fig_comp.update_layout(yaxis_title="비율 (%)", height=400)
    st.plotly_chart(fig_comp, use_container_width=True)

st.divider()

# --- 4. 선택형 워드클라우드 ---
st.subheader("☁️ 감정 그룹별 핵심 키워드 (워드클라우드)")
wc_target = st.selectbox("워드클라우드 대상 그룹 선택", ["전체", "긍정", "부정", "그외"])

# 필터링 및 키워드 추출
if wc_target == "전체":
    wc_df = df
else:
    wc_df = df[df['sentiment_group'] == wc_target]

all_kws = []
for k in wc_df['keywords'].dropna():
    all_kws.extend(k)

# 감탄사 등 한 번 더 필터링 (필요시)
filtered_kws = [word for word in all_kws if len(word) > 1]

if filtered_kws:
    font_paths = ['/System/Library/Fonts/Supplemental/AppleGothic.ttf', '/Library/Fonts/NanumGothic.ttf', 'C:/Windows/Fonts/malgun.ttf']
    selected_font = next((fp for fp in font_paths if os.path.exists(fp)), None)
    
    wc_color = "Greens" if wc_target == "긍정" else "Reds" if wc_target == "부정" else "Purples"
    wc = WordCloud(font_path=selected_font, width=1200, height=400, 
                   background_color='white', colormap=wc_color).generate(" ".join(filtered_kws))
    st.image(wc.to_image(), use_container_width=True)
    
    # 키워드 Top 10 차트도 같이 보여주기
    st.caption(f"📌 {wc_target} 댓글의 주요 키워드 TOP 10")
    top_10 = Counter(filtered_kws).most_common(10)
    t10_df = pd.DataFrame(top_10, columns=['단어', '빈도'])
    fig_t10 = px.bar(t10_df, x='빈도', y='단어', orientation='h', color='빈도', color_continuous_scale=wc_color)
    fig_t10.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
    st.plotly_chart(fig_t10, use_container_width=True)
else:
    st.info("해당 그룹에 추출된 키워드가 없습니다.")

st.divider()

# --- 상세 데이터 리스트 ---
st.subheader("💬 분석 상세 데이터 탐색")
with st.expander("데이터 보기/숨기기"):
    st.dataframe(
        df[['published_at', 'author', 'content', 'sentiment_group', 'llm_label', 'likes']].sort_values('published_at', ascending=False),
        use_container_width=True
    )

st.caption("Opinion Analysis Project by DeepMind Agentic AI")
