#!/bin/bash
# YouTube 트렌드 자동 수집 스크립트

# 프로젝트 디렉토리
PROJECT_DIR="/Users/baeseungjae/Documents/GitHub/kdt_woongin/youtube_trend_tracker"
SCRIPT_DIR="$PROJECT_DIR/scripts"
LOG_DIR="$PROJECT_DIR/logs"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 로그 파일 (날짜별)
LOG_FILE="$LOG_DIR/collect_$(date +%Y%m%d).log"

# 로그 시작
echo "========================================" >> "$LOG_FILE"
echo "수집 시작: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Python 스크립트 실행 (최근 1일 수집)
# 선택: 3 (최근 N일), 일수: 1, 확인: y
cd "$SCRIPT_DIR"
echo -e "3\n1\ny" | python3 collect.py >> "$LOG_FILE" 2>&1

# 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 수집 성공: $(date)" >> "$LOG_FILE"
else
    echo "❌ 수집 실패: $(date)" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 7일 이상 된 로그 파일 삭제
find "$LOG_DIR" -name "collect_*.log" -mtime +7 -delete
