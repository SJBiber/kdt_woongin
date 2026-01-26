import datetime
import os

# 이 파일은 초보자들이 자동화 기능을 테스트해보기 위해 만든 '안사용 로봇'입니다.
# 실행될 때마다 result.txt 파일에 시간을 기록합니다.

def run_example():
    now = datetime.datetime.now()
    log_msg = f"✅ 로봇 출근 완료! (기록 시간: {now.strftime('%Y-%m-%d %H:%M:%S')})\n"
    
    # 결과를 파일로 남깁니다.
    with open("result.txt", "a", encoding="utf-8") as f:
        f.write(log_msg)
    
    print(log_msg)
    print("--------------------------------------------------")
    print("축하합니다! 프로그램이 자동으로 실행되었습니다.")
    print("현재 폴더의 'result.txt' 파일을 열어서 기록을 확인해보세요!")

if __name__ == "__main__":
    run_example()
