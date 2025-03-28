#!/bin/bash
echo "🟢 啟動錄音 + GPS 紀錄"
cd "$(dirname "$0")"
python3 record_with_gps.py
