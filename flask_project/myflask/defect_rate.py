import pandas as pd
import sys
import datetime

# ANSI escape code for green text
GREEN = "\033[92m"
RESET = "\033[0m"

# Load data
df = pd.read_csv('data.csv')

# 생산 시간 : 1분
times = 1
# 하루 생산량 : 1440개
items = 1440


# Start time
start_time = datetime.datetime.now()

while True:
    # Get current date and time
    current_time = datetime.datetime.now()
    
    # Calculate time difference
    time_difference = current_time - start_time

    # Check if 10 seconds have passed
    if time_difference.total_seconds() >= 10:
        # total
        total_items = df['id'].count()
        # defection
        fail_items = df[df['QC'] == 'FAIL']['id'].count()
        # calculate
        failure_rate = (fail_items / total_items) * 100
        # remain item
        remain_items = items - total_items
        # Output the information
        sys.stdout.write(f"{GREEN}==========================1번 생산라인=============================={RESET}\n")
        sys.stdout.write(f"{GREEN}날짜 : {current_time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
        sys.stdout.write(f"{GREEN}1개당 생산 시간 : {times}{RESET}\n")
        sys.stdout.write(f"{GREEN}하루 목표 생산량 : {items}{RESET}\n")
        sys.stdout.write(f"{GREEN}현재 생산된 물품 개수: {total_items}{RESET}\n")
        sys.stdout.write(f"{GREEN}남은 생산량: {remain_items}{RESET}\n")
        sys.stdout.write(f"{GREEN}불량품 개수: {fail_items}{RESET}\n")
        sys.stdout.write(f"{GREEN}불량률: {failure_rate:.2f}%{RESET}\n")
        sys.stdout.write(f"{GREEN}==================================================================={RESET}\n")
        sys.stdout.write(f"{GREEN}{RESET}\n")

        # Update start time
        start_time = current_time
