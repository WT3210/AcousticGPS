#!/bin/bash
echo "🔄 自動推送 AcousticRecorder 程式碼到 GitHub..."
git add *.py *.sh
git commit -m "auto: update code on $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
