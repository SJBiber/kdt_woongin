import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src를 모듈로 인식하기 위해 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database import SupabaseManager

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    st.set_page_config(page_title="Naver Blog Trend Dashboard - Maratang", layout="wide")
    
    st.title("📊 네이버 블로그 포스팅 트렌드 대시보드 (마라탕)")
    st.markdown("---")

    try:
        db = SupabaseManager()
    except Exception as e:
        st.error(f"Supabase 연결 오류: {e}")
        return

    # 데이터 불러오기
    with st.spinner('데이터를 불러오는 중...'):
        # DB에 적재된 모든 키워드 목록 가져오기
        kw_response = db.supabase.table("maratang_blog_trends").select("keyword").execute()
        all_keywords = sorted(list(set([item['keyword'] for item in kw_response.data])))
        
        if not all_keywords:
            st.warning("DB에 데이터가 없습니다. 수집을 먼저 진행해주세요.")
            return

        # 키워드 선택 (멀티 셀렉트)
        default_val = ["마라탕"] if "마라탕" in all_keywords else [all_keywords[0]]
        
        selected_keywords = st.sidebar.multiselect(
            "분석할 키워드를 선택하세요",
            options=all_keywords,
            default=default_val
        )

        if not selected_keywords:
            st.warning("분석할 키워드를 하나 이상 선택해주세요.")
            return

        # 선택된 키워드 데이터 조회
        response = db.supabase.table("maratang_blog_trends")\
            .select("*")\
            .in_("keyword", selected_keywords)\
            .order("date")\
            .execute()
        data = response.data

    if not data:
        st.warning("선택한 키워드에 대한 데이터가 DB에 없습니다.")
        return

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['date', 'keyword'])

    # 필터 및 지표
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("분석 키워드 수", f"{len(selected_keywords)}개")
    with col2:
        st.metric("총 포스팅 수 (합계)", f"{df['total_count'].sum():,}건")
    with col3:
        st.metric("일평균 포스팅 (합계)", f"{df['total_count'].mean() * len(selected_keywords):.1f}건")

    st.markdown(f"### 📈 {', '.join(selected_keywords)} 포스팅 트렌드")
    
    chart_type = st.sidebar.radio("차트 종류", ["라인 차트", "바 차트"])
    
    if chart_type == "바 차트":
        fig = px.bar(
            df, 
            x='date', 
            y='total_count',
            color='keyword',
            barmode='group',
            title="키워드별 일별 포스팅 개수 비교",
            labels={'date': '날짜', 'total_count': '포스팅 개수', 'keyword': '키워드'},
            template="plotly_dark"
        )
    else:
        fig = px.line(
            df, 
            x='date', 
            y='total_count',
            color='keyword',
            title="키워드별 일별 포스팅 개수 추이",
            labels={'date': '날짜', 'total_count': '포스팅 개수', 'keyword': '키워드'},
            template="plotly_dark",
            render_mode="svg"
        )
    
    fig.update_layout(
        xaxis_tickformat='%Y-%m-%d',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 상세 데이터 확인"):
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
