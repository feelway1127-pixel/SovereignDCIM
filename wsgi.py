"""wsgi.py — Render 등 PaaS에서 gunicorn이 이 파일을 통해 앱을 로드합니다."""
from app import app

if __name__ == "__main__":
    app.run()
