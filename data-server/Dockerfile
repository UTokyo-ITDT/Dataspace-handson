FROM python:3.11-slim

WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY main.py .
COPY static/ ./static/
COPY sample_data/ ./sample_data/

# ポート8000を公開
EXPOSE 8000

# アプリケーションを起動
CMD ["python", "main.py"]