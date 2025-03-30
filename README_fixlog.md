# AcousticGPS Update Log

## ❗ 問題描述
在 GPS 狀態已經 fix 成功（如 gpsmon 顯示 Mode: A3, GGA Quality: 2, PRN/Sat數充足）下，`record_with_gps.py` 仍顯示「❌ 超過 60 秒仍無 GPS fix」。

## 🔍 問題原因
原始程式僅依據「衛星數 >= 4」進行 GPS fix 判斷，忽略 `$GPGGA` 中的 fix quality 及 `$GPRMC` 的有效狀態欄位，導致誤判。

## ✅ 改進方法
更新版 `record_with_gps.py`：
1. 同時確認 `$GPGGA` 的 fix quality 欄位為 1 或 2（代表標準或 DGPS fix）
2. 確認 `$GPRMC` 中定位狀態為 A（有效）
3. 衛星數量仍保留作為輔助條件

## 📦 打包內容
- record_with_gps.py（最新版）
- run.sh
- README（即本檔案）
