# Dockerfile

# 1. 使用 Python 3.11 作為基礎
FROM python:3.11-slim

# 2. 建立工作目錄
WORKDIR /app

# 3. 複製 requirements.txt
COPY ./requirements.txt /app/requirements.txt

# 4. 安裝所有 Python 依賴
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 5. 複製應用程式程式碼
COPY ./app /app/app
COPY ./scripts /app/scripts

# 6. 指定啟動指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]