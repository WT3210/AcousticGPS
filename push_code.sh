#!/bin/bash
echo "🔁 將最新程式碼同步至 GitHub..."
git add *.py *.sh
git commit -m "auto: update code on $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
