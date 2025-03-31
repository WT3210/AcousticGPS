# 📦 AcousticGPS 打包與版本管理規範

## 🔖 版本編號
- 使用格式：`MMDD_HHMM`
- 寫入至 `record_with_gps.py` 第一行，例如：
  ```python
  # Version: 0330_1732 | Generated: 2025-03-30 17:32:43
  ```

---

## 📂 打包檔案內容（固定三檔）
| 檔案 | 說明 |
|------|------|
| `record_with_gps.py` | 主程式，含錄音、GPS 同步與即時顯示邏輯，開頭標記版本與產生時間。 |
| `run.sh`             | 啟動腳本，會自動停用 `gpsd` 並執行主程式。 |
| `upDATELOG.md`       | 所有版本的更新紀錄。**每次更新都插在最上方**（保留歷史）。 |

---

## 📒 upDATELOG.md 管理規則
- 檔名固定為：`upDATELOG.md`
- 每次打包都會在最上方新增一段版本記錄，如下範例：
  ```markdown
  ## 🕒 更新時間：2025-03-30 17:32:43 | 版本：0330_1732
  - 🎯 GPS Fix 條件：fix quality >= 1 且衛星數 >= 4
  - 📡 即時顯示經緯度、海拔、衛星數、速度、錄音秒數
  ---
  ```

---

## 📦 壓縮檔命名規則
- 格式：`AcousticGPS_YYYYMMDD_HHMMSS.zip`
- 例如：`AcousticGPS_20250330_173243.zip`

---

## ⚙️ 功能與記錄演進（目前版本功能）
- ✅ GPS fix 成功才開始錄音與記錄 GPX
- ✅ 若未 fix，自動等待（最多 60 秒）
- ✅ 每秒記錄一次點位，輸出 `.gpx`
- ✅ 錄音支援 `arecord` 高取樣率
- ✅ 即時顯示：
  - 錄音秒數
  - 經緯度
  - 海拔
  - 衛星數
  - 速度（km/h）

---

## 🗂️ 設備對應（參考）

| 階段 | 設備組合 | 說明 |
|------|----------|------|
| 一   | Arduino Nano 33 BLE + GPS + SD | BLE 控制錄音、記錄 GPX，適合低功耗 |
| 二   | Raspberry Pi Zero / 5 + I2S 麥克風 + GPS | 高頻錄音 + 位置同步 |
| 三   | Pico W 2 + LoRa + GPS（暫停） | 水下聲音監測，受限於功耗與記憶體 |

📎 參考檔案：`TinyML_GPS_Device_Stages_Detailed.md`

---
