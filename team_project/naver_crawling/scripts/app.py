import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src를 모듈로 인식하기 위해 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database import SupabaseClient

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    st.set_page_config(page_title="Naver Blog Trend Dashboard", layout="wide")
    
    st.title("📊 네이버 블로그 포스팅 트렌드 대시보드")
    st.markdown("---")

    try:
        db = SupabaseClient()
    except Exception as e:
        st.error(f"Supabase 연결 오류: {e}")
        return

    # 데이터 불러오기
    with st.spinner('데이터를 불러오는 중...'):
        # DB에 적재된 모든 키워드 목록 가져오기
        kw_response = db.supabase.table("naver_blog_counts").select("keyword").execute()
        all_keywords = sorted(list(set([item['keyword'] for item in kw_response.data])))
        
        # 키워드 선택 (멀티 셀렉트)
        selected_keywords = st.sidebar.multiselect(
            "분석할 키워드를 선택하세요",
            options=all_keywords,
            default=[all_keywords[0]] if all_keywords else []
        )

        if not selected_keywords:
            st.warning("분석할 키워드를 하나 이상 선택해주세요.")
            return

        # 선택된 키워드 데이터 조회
        response = db.supabase.table("naver_blog_counts")\
            .select("*")\
            .in_("keyword", selected_keywords)\
            .order("target_date")\
            .execute()
        data = response.data

    if not data:
        st.warning("선택한 키워드에 대한 데이터가 DB에 없습니다.")
        return

    df = pd.DataFrame(data)
    df['target_date'] = pd.to_datetime(df['target_date'])
    df = df.sort_values(['target_date', 'keyword'])

    # 필터 및 지표 (선택된 키워드 합계 기준)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("분석 키워드 수", f"{len(selected_keywords)}개")
    with col2:
        st.metric("총 포스팅 수 (합계)", f"{df['post_count'].sum():,}건")
    with col3:
        st.metric("일평균 포스팅 (합계)", f"{df['post_count'].mean() * len(selected_keywords):.1f}건")

    st.markdown(f"### 📈 {', '.join(selected_keywords)} 포스팅 트렌드")
    
    # Plotly 차트 생성 (멀티 키워드 비교를 위해 라인 차트 또는 그룹 바 차트)
    chart_type = st.sidebar.radio("차트 종류", ["바 차트", "라인 차트"])
    
    if chart_type == "바 차트":
        fig = px.bar(
            df, 
            x='target_date', 
            y='post_count',
            color='keyword',
            barmode='group',
            title="키워드별 일별 포스팅 개수 비교",
            labels={'target_date': '날짜', 'post_count': '포스팅 개수', 'keyword': '키워드'},
            template="plotly_dark"
        )
    else:
        fig = px.line(
            df, 
            x='target_date', 
            y='post_count',
            color='keyword',
            title="키워드별 일별 포스팅 개수 추이",
            labels={'target_date': '날짜', 'post_count': '포스팅 개수', 'keyword': '키워드'},
            template="plotly_dark",
            render_mode="svg"
        )
    
    fig.update_layout(
        xaxis_tickformat='%Y-%m-%d',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 상세 데이터 테이블
    with st.expander("📄 상세 데이터 확인"):
        st.dataframe(df.sort_values('target_date', ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
