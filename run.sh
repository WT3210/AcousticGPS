#!/bin/bash
echo "🟢 啟動錄音 + GPS 紀錄"

# 啟動 GPSD（每次強制重啟）
echo "🛰 啟動 GPS 服務..."
sudo killall gpsd 2>/dev/null
sudo gpsd /dev/serial0 -F /var/run/gpsd.sock

# 開始錄音 + GPX
python3 record_with_gps.py
