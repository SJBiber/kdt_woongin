import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class YoutubeDataViewer:
    """
    유튜브 검색 결과 CSV 파일을 표(Table) 형식으로 보여주는 GUI 뷰어 클래스입니다.
    데이터 필터링, 정렬, 비디오 링크 열기 기능을 제공합니다.
    """
    def __init__(self, root, file_path):
        """
        초기화 메서드
        :param root: Tkinter 메인 윈도우 객체
        :param file_path: 읽어올 CSV 파일 경로
        """
        self.root = root
        self.root.title("YouTube Search Results Viewer")
        self.root.geometry("1000x600")
        
        self.file_path = file_path
        self.df = None          # 전체 데이터 보관용
        self.filtered_df = None # 필터링/정렬된 데이터 보관용
        
        self.setup_styles()     # UI 스타일 설정
        self.create_widgets()   # 위젯 생성
        self.load_data()        # CSV 데이터 로드

    def setup_styles(self):
        """UI 컴포넌트(Treeview 등)의 테마와 스타일을 설정합니다."""
        style = ttk.Style()
        style.theme_use('clam') # 깔끔한 테마 적용
        
        # 표(Treeview) 스타일 설정
        style.configure("Treeview", 
                        background="#ffffff", 
                        foreground="#333333", 
                        rowheight=25, 
                        fieldbackground="#ffffff",
                        font=('Arial', 10))
        
        # 선택된 행의 색상 설정
        style.map("Treeview", 
                  background=[('selected', '#347083')],
                  foreground=[('selected', '#ffffff')])
        
        # 헤더 스타일 설정
        style.configure("Treeview.Heading", 
                        font=('Arial', 11, 'bold'),
                        background="#f0f0f0",
                        foreground="#333333")

    def create_widgets(self):
        """검색창, 표, 스크롤바 등 UI 요소를 생성합니다."""
        # --- 상단 검색 및 정보 영역 ---
        top_frame = tk.Frame(self.root, pady=10, padx=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="검색 (제목):", font=('Arial', 10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        # 입력값이 변할 때마다 filter_data 함수 실행
        self.search_var.trace_add("write", self.filter_data)
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        
        self.info_label = tk.Label(top_frame, text="데이터: 0건", font=('Arial', 10, 'italic'))
        self.info_label.pack(side=tk.RIGHT)

        # --- 중앙 데이터 표(Treeview) 영역 ---
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 세로 및 가로 스크롤바
        tree_scroll_y = ttk.Scrollbar(table_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 표 객체 생성 (5개 열 설정)
        self.columns = ("video_id", "title", "published_at", "channel_title", "view_count")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show='headings',
                                 yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 각 열의 제목 설정 및 클릭 시 정렬 기능 연결
        self.tree.heading("video_id", text="영상 ID", command=lambda: self.sort_by("video_id"))
        self.tree.heading("title", text="영상 제목", command=lambda: self.sort_by("title"))
        self.tree.heading("published_at", text="등록일", command=lambda: self.sort_by("published_at"))
        self.tree.heading("channel_title", text="채널명", command=lambda: self.sort_by("channel_title"))
        self.tree.heading("view_count", text="조회수", command=lambda: self.sort_by("view_count"))

        # 각 열의 너비 및 정렬 설정
        self.tree.column("video_id", width=120)
        self.tree.column("title", width=400)
        self.tree.column("published_at", width=100)
        self.tree.column("channel_title", width=150)
        self.tree.column("view_count", width=100, anchor=tk.E) # 조회수는 오른쪽 정렬
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # 마우스 더블클릭 이벤트 연결 (영상 열기)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # 하단 도움말
        footer_label = tk.Label(self.root, text="행을 더블 클릭하면 브라우저에서 해당 영상을 엽니다.", 
                                fg="gray", font=('Arial', 9))
        footer_label.pack(pady=5)

    def load_data(self):
        """CSV 파일을 읽어 데이터프레임에 저장하고 표에 표시합니다."""
        try:
            if not os.path.exists(self.file_path):
                messagebox.showerror("오류", f"파일을 찾을 수 없습니다: {self.file_path}")
                return
            
            # CSV 로드
            self.df = pd.read_csv(self.file_path)
            # 조회수 컬럼을 숫자로 변환 (정렬을 위해 필수)
            self.df['view_count'] = pd.to_numeric(self.df['view_count'], errors='coerce').fillna(0).astype(int)
            self.filtered_df = self.df.copy()
            self.update_treeview(self.filtered_df)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 로드 중 오류 발생: {e}")

    def update_treeview(self, dataframe):
        """전달받은 데이터프레임 내용을 화면의 표에 다시 그립니다."""
        # 기존 내용 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 새 데이터 추가
        for _, row in dataframe.iterrows():
            self.tree.insert("", tk.END, values=list(row))
        
        # 상태 표시 업데이트
        self.info_label.config(text=f"데이터: {len(dataframe)}건")

    def filter_data(self, *args):
        """검색창 입력값에 따라 제목을 필터링합니다."""
        search_term = self.search_var.get()
        if self.df is not None:
            # 제목에 검색어가 포함된 행만 추출 (대소문자 구분 없음)
            self.filtered_df = self.df[self.df['title'].str.contains(search_term, case=False, na=False)]
            self.update_treeview(self.filtered_df)

    def sort_by(self, col):
        """
        열 헤더 클릭 시 해당 열을 기준으로 정렬합니다. 
        클릭할 때마다 오름차순/내림차순이 토글됩니다.
        """
        if self.filtered_df is not None:
            # 현재 정렬 상태를 체크하여 토글
            ascending = getattr(self, f"_sort_{col}", True)
            setattr(self, f"_sort_{col}", not ascending)
            
            self.filtered_df = self.filtered_df.sort_values(by=col, ascending=ascending)
            self.update_treeview(self.filtered_df)

    def on_item_double_click(self, event):
        """선택된 행의 비디오 ID를 추출하여 유튜브 URL을 브라우저에 엽니다."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            video_id = self.tree.item(item, "values")[0]
            url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(url)

if __name__ == "__main__":
    import sys
    
    # 기본 파일 경로 설정
    csv_path = "/Users/baeseungjae/Documents/GitHub/kdt_woongin/ai/api/youtube_주식_results.csv"
    
    # 실행 인자로 파일 경로가 들어오면 해당 경로 사용
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    # GUI 실행
    root = tk.Tk()
    app = YoutubeDataViewer(root, csv_path)
    root.mainloop()
