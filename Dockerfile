# --- Stage 1: 빌드 단계 ---
FROM python:3.11-slim AS builder
WORKDIR /app

# 가상환경 생성 및 의존성 설치
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: 실행 단계 ---
FROM python:3.11-slim
WORKDIR /app

# 1. 빌드 단계에서 생성된 가상환경 폴더만 통째로 복사
COPY --from=builder /opt/venv /opt/venv

# 2. 가상환경 내의 bin 폴더를 PATH에 추가 (이러면 python, uvicorn 등을 바로 사용 가능)
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 소스 코드 복사
COPY . .

EXPOSE 8000

# 4. 실행 (가상환경의 PATH가 잡혀있으므로 바로 실행 가능)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
