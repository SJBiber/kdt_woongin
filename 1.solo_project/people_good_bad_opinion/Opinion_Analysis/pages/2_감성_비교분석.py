import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="감성 비교분석", page_icon="2️⃣", layout="wide")

# 환경 변수 로드
load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@st.cache_data(ttl=300)
def load_comparison_data():
    """임성근/백종원 데이터 로드 및 전처리"""
    client = get_supabase_client()
    
    # 헬퍼 함수: 데이터 로드
    def fetch_all(table):
        data = []
        offset = 0
        limit = 1000
        while True:
            res = client.table(table).select("*").range(offset, offset + limit - 1).execute()
            if not res.data: break
            data.extend(res.data)
            if len(res.data) < limit: break
            offset += limit
        return pd.DataFrame(data)

    df_im = fetch_all("im_sung_gen_youtube_comments")
    df_baek = fetch_all("baek_jongwon_youtube_comments")
    
    # 전처리 및 감정 라벨링
    label_map = {0: "지지", 1: "분노", 2: "중립", 3: "실망", 4: "조롱", 5: "그외"}
    
    def process_df(df, name):
        if df.empty: return df
        df['published_at'] = pd.to_datetime(df['published_at'])
        df = df.drop_duplicates(subset=['comment_id'], keep='first')
        df['llm_label'] = df['llm_sentiment'].map(label_map)
        df['target'] = name
        df['content_length'] = df['content'].fillna('').str.len()
        return df

    df_im = process_df(df_im, "임성근")
    df_baek = process_df(df_baek, "백종원")
    
    # 임성근 데이터 필터링 (논란 후: 2026-01-19 ~)
    controversy_date = pd.Timestamp("2026-01-19")
    if df_im['published_at'].dt.tz is not None:
        controversy_date = controversy_date.tz_localize('UTC')
    
    df_im = df_im[df_im['published_at'] >= controversy_date]
    
    return df_im, df_baek

# 데이터 로드
df_im, df_baek = load_comparison_data()

if df_im.empty or df_baek.empty:
    st.error("데이터가 부족하여 비교 분석을 진행할 수 없습니다. (임성근 논란 후 데이터 없음)")
    st.stop()

# --- 헤더 ---
st.title("2️⃣ 감성 비교분석 (vs 백종원)")
st.markdown("""
### 두 사건의 여론 반응은 어떻게 다른가?
**임성근(논란 후)** vs **백종원** 사례를 비교하여, 대중이 느끼는 **감정의 질감(Sentiment Texture)** 차이를 분석합니다.
""")

st.markdown("---")

# 색상 맵 정의
emotion_colors = {
    "지지": "#00CC96", "분노": "#EF553B", "중립": "#636EFA",
    "실망": "#FFA15A", "조롱": "#AB63FA", "그외": "#B6E880"
}

# --- 1. 감정 분포 비교 (Pie Chart) ---
st.subheader("📊 감정 분포 비교")

col1, col2 = st.columns(2)

def draw_pie(df, title):
    counts = df['llm_label'].value_counts().reset_index()
    counts.columns = ['Sentiment', 'Count']
    fig = px.pie(
        counts, values='Count', names='Sentiment',
        color='Sentiment', color_discrete_map=emotion_colors,
        hole=0.4, title=title,
        labels={'Sentiment': '감정', 'Count': '댓글 수'}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

with col1:
    st.plotly_chart(draw_pie(df_im, "임성근 (논란 후) 감정 분포"), width="stretch")

with col2:
    st.plotly_chart(draw_pie(df_baek, "백종원 감정 분포"), width="stretch")

# --- 2. 주요 감정 랭킹 ---
st.markdown("#### 💡 감정 비교 인사이트")
im_top = df_im['llm_label'].mode()[0]
baek_top = df_baek['llm_label'].mode()[0]

st.info(f"""
- **임성근**의 경우 **'{im_top}'** 감정이 가장 지배적입니다. (개인적 실망과 비판)
- **백종원**의 경우 **'{baek_top}'** 감정이 가장 지배적입니다. (사업적 비판 및 옹호 혼재)
""")

st.markdown("---")

# --- 3. 감정별 영향력 비교 (평균 좋아요) ---
st.subheader("⭐ 감정별 공감도(좋아요) 비교")
st.markdown("> 어떤 감정의 댓글이 사람들의 공감을 가장 많이 얻고 있을까요? (평균 좋아요 수 분석)")

col_l1, col_l2 = st.columns(2)

def draw_likes_bar(df, title, target_name):
    likes_df = df.groupby('llm_label')['likes'].mean().reset_index()
    likes_df.columns = ['Sentiment', 'Avg Likes']
    
    fig = px.bar(
        likes_df,
        x='Sentiment',
        y='Avg Likes',
        color='Sentiment',
        color_discrete_map=emotion_colors,
        text_auto='.1f',
        title=f"{target_name} 감정별 평균 좋아요",
        labels={'Sentiment': '감정', 'Avg Likes': '평균 좋아요 수'}
    )
    fig.update_traces(textposition='outside', cliponaxis=False)
    fig.update_layout(showlegend=False, height=400, yaxis_title="평균 좋아요 수", yaxis_range=[0, likes_df['Avg Likes'].max() * 1.15])
    return fig

with col_l1:
    st.plotly_chart(draw_likes_bar(df_im, "임성근 감정별 공감도", "임성근 (논란 후)"), use_container_width=True)

with col_l2:
    st.plotly_chart(draw_likes_bar(df_baek, "백종원 감정별 공감도", "백종원"), use_container_width=True)

st.markdown("---")

# --- 4. 감정에 따른 텍스트 밀도 (댓글 길이) 비교 ---
st.subheader("📝 감정에 따른 텍스트 밀도 (댓글 길이) 비교")
st.markdown("> 사람들은 어떤 감정을 표현할 때 더 길고 자세하게 글을 쓸까요? (평균 글자 수 분석)")

col_d1, col_d2 = st.columns(2)

def draw_density_bar(df, title, target_name):
    density_df = df.groupby('llm_label')['content_length'].mean().reset_index()
    density_df.columns = ['Sentiment', 'Avg Length']
    
    # 순서 고정 (지지~그외)
    sentiment_order = ["지지", "분노", "중립", "실망", "조롱", "그외"]
    density_df['Sentiment'] = pd.Categorical(density_df['Sentiment'], categories=sentiment_order, ordered=True)
    density_df = density_df.sort_values('Sentiment')
    
    fig = px.bar(
        density_df,
        x='Sentiment',
        y='Avg Length',
        color='Sentiment',
        color_discrete_map=emotion_colors,
        text_auto='.1f',
        title=f"{target_name} 감정별 평균 글자 수",
        labels={'Sentiment': '감정', 'Avg Length': '평균 글자 수'}
    )
    fig.update_traces(textposition='outside', cliponaxis=False)
    fig.update_layout(showlegend=False, height=400, yaxis_title="평균 글자 수", yaxis_range=[0, density_df['Avg Length'].max() * 1.15])
    return fig

with col_d1:
    st.plotly_chart(draw_density_bar(df_im, "임성근 감정별 텍스트 밀도", "임성근 (논란 후)"), use_container_width=True)

with col_d2:
    st.plotly_chart(draw_density_bar(df_baek, "백종원 감정별 텍스트 밀도", "백종원"), use_container_width=True)

st.markdown("""
> **인사이트**:
> - 일반적으로 **'실망'**이나 **'중립적 비판'**은 논리적인 근거를 제시하느라 댓글이 길어지는 경향이 있습니다.
> - 반면 **'분노'**나 **'조롱'**은 짧고 강렬한 단어나 밈(Meme) 위주일 때 길이가 상대적으로 짧을 수 있습니다.
""")

st.markdown("""
> **분석 마스터의 팁**: 특정 감정의 '평균 좋아요'가 높다는 것은 대중이 해당 의견에 강력하게 동조하고 있음을 의미합니다. 
> 예를 들어 '분노'의 좋아요가 압도적이라면 여론이 매우 격앙된 상태이며, '지지'의 좋아요가 높다면 핵심 팬덤이 결집하고 있다는 신호입니다.
""")

st.markdown("---")

# --- 4. 가장 핵심적인 공감 댓글 (Top 1) ---
st.subheader("� 핵심 공감 댓글 (Best vs Best)")
st.markdown("> 대중의 공감이 가장 집중된 'Top 1 감정'의 대표 댓글입니다.")

col_b1, col_b2 = st.columns(2)

def display_top_one_comment(df, target_name):
    # 1. 감정별 평균 좋아요 계산하여 가장 높은 감정 추출
    avg_likes = df.groupby('llm_label')['likes'].mean()
    if avg_likes.empty:
        return
        
    top_sentiment = avg_likes.idxmax() # 평균 좋아요 1위 감정
    color = emotion_colors.get(top_sentiment, "#333")
    
    st.markdown(f"#### {target_name} : **{top_sentiment}**")
    
    # 2. 해당 감정군에서 실제 좋아요가 가장 많은 댓글 1건 추출
    subset = df[df['llm_label'] == top_sentiment]
    if not subset.empty:
        top_row = subset.sort_values('likes', ascending=False).iloc[0]
        st.markdown(f"""
            <div style="border-left: 6px solid {color}; padding: 15px; background-color: #f8f9fa; border-radius: 0 10px 10px 0; box-shadow: 3px 3px 10px rgba(0,0,0,0.07);">
                <div style="margin-bottom: 8px;">
                    <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{top_sentiment} 1위</span>
                    <span style="font-size: 0.9em; font-weight: bold; color: {color}; margin-left: 10px;">👍 {int(top_row['likes']):,} Likes</span>
                </div>
                <div style="font-size: 1.05em; font-weight: 500; color: #111; line-height: 1.6; margin-bottom: 10px;">"{top_row['content']}"</div>
                <div style="font-size: 0.85em; color: #777; text-align: right;">- {top_row['author']}</div>
            </div>
        """, unsafe_allow_html=True)

with col_b1:
    display_top_one_comment(df_im, "임성근 (논란 후)")

with col_b2:
    display_top_one_comment(df_baek, "백종원")

st.markdown("---")

# --- 4. 가설 검증: 조롱 vs 분노 ---
st.subheader("🔎 가설 검증: 분노인가, 조롱인가?")

st.markdown("""
**가설**: 범죄 성격(음주운전)인 임성근 사례는 **'조롱'**보다는 점잖은 **'실망/분노'**가 주를 이룰 것이며, 
사업적 논란인 백종원 사례와는 다른 감정 양상을 보일 것이다.
""")

# 비율 계산
def get_ratio(df, label):
    return (df['llm_label'] == label).mean() * 100

im_anger = get_ratio(df_im, "분노")
im_sarcasm = get_ratio(df_im, "조롱")
baek_anger = get_ratio(df_baek, "분노")
baek_sarcasm = get_ratio(df_baek, "조롱")

col_h1, col_h2 = st.columns(2)

with col_h1:
    st.metric("임성근 분노 vs 조롱", f"{im_anger:.1f}% vs {im_sarcasm:.1f}%", delta=f"{im_anger - im_sarcasm:.1f}%p (분노 우세)" if im_anger > im_sarcasm else f"{im_sarcasm - im_anger:.1f}%p (조롱 우세)")

with col_h2:
    st.metric("백종원 분노 vs 조롱", f"{baek_anger:.1f}% vs {baek_sarcasm:.1f}%", delta=f"{baek_anger - baek_sarcasm:.1f}%p (분노 우세)" if baek_anger > baek_sarcasm else f"{baek_sarcasm - baek_anger:.1f}%p (조롱 우세)")

# --- 5. 키워드 비교 ---
st.markdown("---")
st.subheader("🔑 주요 키워드 Top 10 비교")

def get_top_keywords(df):
    all_kws = []
    for k in df['keywords'].dropna():
        all_kws.extend(k)
    return [w for w, c in Counter([w for w in all_kws if len(w)>1]).most_common(10)]

col_k1, col_k2 = st.columns(2)

with col_k1:
    st.markdown("**임성근 주요 키워드**")
    st.write(", ".join(get_top_keywords(df_im)))

with col_k2:
    st.markdown("**백종원 주요 키워드**")
    st.write(", ".join(get_top_keywords(df_baek)))
