#!/bin/bash
echo "🟢 啟動錄音 + GPS 紀錄"

# 設定參數
DURATION=60
SAMPLERATE=44100
CHANNELS=1
DEVICE="plughw:0,0"
FILENAME="record_$(date +%m%d_%H%M)"
LOGDIR="./logs"
mkdir -p $LOGDIR

echo "🔎 檢查錄音裝置是否存在..."
arecord -l | grep -q "card 0: wm8960soundcard"
if [ $? -ne 0 ]; then
  echo "❌ 錄音裝置未偵測到，請確認 WM8960 是否接好並啟用！"
  exit 1
fi

echo "🎙 開始錄音 $DURATION 秒..."
arecord -D $DEVICE -f S16_LE -r $SAMPLERATE -c $CHANNELS -d $DURATION "$LOGDIR/$FILENAME.wav" &
PID_RECORD=$!

sleep 2

echo "🛰 同步啟動 GPS 記錄..."
python3 record_with_gps.py --duration $DURATION --output "$LOGDIR/$FILENAME.gpx" &
PID_GPS=$!

wait $PID_RECORD
wait $PID_GPS

WAVSIZE=$(stat -c%s "$LOGDIR/$FILENAME.wav")
if [ "$WAVSIZE" -le 100 ]; then
  echo "⚠️ 錄音異常：檔案僅 $WAVSIZE bytes，可能無聲！"
else
  echo "✅ 錄音完成，大小 $WAVSIZE bytes"
fi

echo "📁 已儲存：$LOGDIR/$FILENAME.wav 與 $LOGDIR/$FILENAME.gpx"