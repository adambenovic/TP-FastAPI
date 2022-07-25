pwd
pip install -r requirements.txt
docker-compose up -d
export $(grep -v '^#' .env | xargs)
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --reload
