# Python 3.11 slim 버전 기반 이미지 사용
FROM python:3.11-slim

# 컨테이너 내 작업 디렉토리 생성 및 이동
WORKDIR /app

# requirements.txt 복사 후 패키지 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 전체 복사
COPY . .

# 8000번 포트 개방
EXPOSE 8000

# Django 개발 서버 실행 (0.0.0.0:8000)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
