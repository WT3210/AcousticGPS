import os
import time
import argparse
import subprocess
from datetime import datetime

# 解析參數
parser = argparse.ArgumentParser()
parser.add_argument('--duration', type=int, default=60, help='錄音時間（秒）')
parser.add_argument('--output', type=str, required=True, help='GPX 輸出路徑')
args = parser.parse_args()

# 啟動 GPS 紀錄
print("📡 GPS 紀錄開始")
gps_cmd = ["gpspipe", "-w", "-o", args.output]
gps_proc = subprocess.Popen(gps_cmd)

# 持續錄音時間
time.sleep(args.duration)

# 停止
gps_proc.terminate()
print("🛰 GPS 紀錄結束")