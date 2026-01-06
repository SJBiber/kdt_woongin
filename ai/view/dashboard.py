import os
import re
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Mac 환경에서 한글 폰트(AppleGothic) 설정 및 마이너스 기호 깨짐 방지
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class YoutubeAnalyticsDashboard:
    """
    유튜브 검색 결과 데이터를 시각화하여 일별 조회수를 바 그래프로 보여주는 대시보드 클래스입니다.
    파일 로드, 차트 갱신, 마우스 호버 이벤트를 관리합니다.
    """
    def __init__(self, root):
        """
        초기화 메서드
        :param root: Tkinter 메인 윈도우 객체
        """
        self.root = root
        self.root.title("YouTube Daily View Analytics")
        self.root.geometry("1100x750")
        
        self.current_file = None
        self.all_dates = [] # 툴팁용 전체 날짜를 저장 (X축 라벨이 숨겨져도 호버 시 날짜를 보여줌)
        
        self.setup_ui()

    def setup_ui(self):
        """상단 제목, 제어부, 차트 영역 등 전체 UI 구성을 설정합니다."""
        # --- 헤더 영역 (제목) ---
        header_frame = tk.Frame(self.root, pady=20, bg="#f8f9fa")
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="YouTube 일별 조회수 분석", 
                               font=('Arial', 24, 'bold'), bg="#f8f9fa", fg="#212529")
        title_label.pack()
        
        # --- 제어 영역 (파일 로드) ---
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill=tk.X)
        
        self.file_label = tk.Label(control_frame, text="선택된 파일 없음", font=('Arial', 10), width=60, anchor="e")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        load_btn = ttk.Button(control_frame, text="CSV 파일 불러오기", command=self.load_csv_dialog)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # --- 차트 영역 (Matplotlib 그래프 삽입) ---
        self.chart_frame = tk.Frame(self.root, bg="white")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Matplotlib Figure 객체 생성 및 Canvas 연결
        self.fig = Figure(figsize=(10, 6), dpi=100, tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # 마우스 움직임 감지 이벤트를 on_hover 함수에 연결
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        
        self.tooltip = None # 마우스 호버 시 나타날 툴팁 객체 초기화
        self.bars = None    # 그래프 막대들(Container) 보관용

    def load_csv_dialog(self):
        """파일 탐색기를 열어 분석할 CSV 파일을 선택합니다."""
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="유튜브 결과 CSV 파일 선택",
            filetypes=(("CSV 파일", "*.csv"), ("모든 파일", "*.*"))
        )
        if file_path:
            self.process_and_plot(file_path)

    def process_and_plot(self, file_path):
        """
        선택된 CSV 파일을 읽어 데이터를 가공하고 그래프를 그립니다.
        :param file_path: CSV 파일의 절대 경로
        """
        try:
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            
            # CSV 읽기
            df = pd.read_csv(file_path)
            
            # 필수 컬럼 존재 여부 체크
            required_cols = ['published_at', 'view_count']
            if not all(col in df.columns for col in required_cols):
                messagebox.showerror("오류", f"CSV에 {required_cols} 열이 포함되어야 합니다.")
                return

            # 데이터 가공: 조회수 숫자 변환, 날짜 형식으로 변환
            df['view_count'] = pd.to_numeric(df['view_count'], errors='coerce').fillna(0)
            df['published_at'] = pd.to_datetime(df['published_at']).dt.date
            
            # 날짜별로 그룹화하여 조회수 합계 계산
            daily_stats = df.groupby('published_at')['view_count'].sum().reset_index()
            daily_stats = daily_stats.sort_values('published_at')

            # 파일명에서 키워드 추출 (예: youtube_주식_results -> 주식)
            filename = os.path.basename(file_path)
            keyword_match = re.search(r'youtube_(.*)_results', filename)
            keyword = keyword_match.group(1) if keyword_match else "알 수 없음"

            # 차트 업데이트 호출
            self.update_chart(daily_stats, keyword)

        except Exception as e:
            messagebox.showerror("오류", f"파일 처리 중 오류 발생: {e}")

    def format_view_count(self, n):
        """조회수 숫자를 가독성 좋게 포맷팅합니다 (예: 1,000,000 -> 1.0M)"""
        if n >= 1_000_000:
            return f'{n/1_000_000:.1f}M'
        elif n >= 1_000:
            return f'{n/1_000:.1f}K'
        return str(int(n))

    def update_chart(self, data, keyword):
        """Matplotlib 차트 내용을 새로 그립니다."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # 데이터 포인트 설정
        self.all_dates = [d.strftime('%m-%d') for d in data['published_at']] # 'MM-DD' 형식
        dates = self.all_dates
        views = data['view_count']
        num_bars = len(dates)
        
        # 바 그래프 그리기
        self.bars = ax.bar(dates, views, color='#3498db', edgecolor='#2980b9', alpha=0.8)
        
        # --- 툴팁(호버 팝업) 설정 (초기엔 숨김) ---
        self.tooltip = ax.annotate(
            "", xy=(0, 0), xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9),
            arrowprops=dict(arrowstyle="->"),
            fontsize=10, 
            fontweight='bold'
        )
        self.tooltip.set_visible(False)
        
        # 타이틀 및 축 라벨 설정
        ax.set_title(f"일별 누적 조회수: [{keyword}]", fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel("게시 날짜 (MM-DD)", fontsize=10)
        ax.set_ylabel("총 조회수", fontsize=10)
        
        # X축 라벨 최적화: 개수에 따라 회전 및 표시 간격 조절
        if num_bars > 10:
            rotation = 90 if num_bars > 20 else 45
            ax.tick_params(axis='x', rotation=rotation, labelsize=8)
            
            # 데이터가 너무 많으면 라벨을 띄엄띄엄 표시하여 겹침 방지
            if num_bars > 30:
                for n, label in enumerate(ax.xaxis.get_ticklabels()):
                    if n % (num_bars // 10) != 0:
                        label.set_visible(False)
        
        # Y축 라벨에 콤마(,) 추가 포맷팅
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # 데이터가 적을 때(20개 이하)만 막대 위에 직접 조회수 표시
        if num_bars <= 20:
            font_size = 9
            for bar in self.bars:
                height = bar.get_height()
                if height > 0:
                    label_text = self.format_view_count(height)
                    ax.annotate(label_text,
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', 
                                fontsize=font_size)

        # 격자 및 외곽선 디자인
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 도표 그리기 완료
        self.canvas.draw()

    def on_hover(self, event):
        """
        마우스가 차트 위에서 움직일 때 호출되는 핸들러입니다.
        막대 위에 마우스가 있으면 툴팁을 표시합니다.
        """
        if self.tooltip is None or self.bars is None:
            return
            
        vis = self.tooltip.get_visible()
        if event.inaxes: # 마우스가 차트 영역 안에 있는 경우
            found = False
            for bar in self.bars:
                cont, ind = bar.contains(event) # 마우스가 막대 영역에 포함되는지 확인
                if cont:
                    height = bar.get_height()
                    # 툴팁 위치를 막대 상단으로 이동
                    self.tooltip.xy = (bar.get_x() + bar.get_width()/2, height)
                    
                    # 해당 인덱스의 날짜를 찾아 텍스트 설정
                    try:
                        idx = int(bar.get_x() + 0.5)
                        if 0 <= idx < len(self.all_dates):
                           date_label = self.all_dates[idx]
                           text = f"날짜: {date_label}\n조회수: {int(height):,}회"
                           self.tooltip.set_text(text)
                    except:
                        pass
                        
                    self.tooltip.set_visible(True)
                    found = True
                    break
            
            # 마우스가 막대를 벗어나면 툴팁 숨김
            if not found and vis:
                self.tooltip.set_visible(False)
        else: # 마우스가 차트 영역 밖인 경우
            if vis:
                self.tooltip.set_visible(False)
        
        # 가시성이 변한 경우에만 재그리기 요청
        if vis != self.tooltip.get_visible():
            self.canvas.draw_idle()

if __name__ == "__main__":
    # 메인 윈도우 생성 및 앱 실행
    root = tk.Tk()
    app = YoutubeAnalyticsDashboard(root)
    
    # 프로그램 실행 시 기본 데이터 파일 로드 시도
    initial_path = "/Users/baeseungjae/Documents/GitHub/kdt_woongin/ai/api/youtube_주식_results.csv"
    if os.path.exists(initial_path):
        app.process_and_plot(initial_path)
        
    root.mainloop()
