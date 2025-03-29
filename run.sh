#!/bin/bash

mkdir -p logs

# 自動釋放 /dev/serial0
echo "🧹 停用 gpsd 並釋放 /dev/serial0"
sudo systemctl stop gpsd.socket
sudo systemctl stop gpsd
sudo killall gpsd
sudo fuser -k /dev/serial0 2>/dev/null

echo "🟢 啟動錄音與 GPS 記錄..."
python3 record_with_gps.py
