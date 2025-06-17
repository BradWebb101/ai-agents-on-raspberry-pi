FROM python:3.12-slim

COPY api.py ./
COPY database.db ./

RUN pip install fastapi uvicorn pydantic

RUN chmod a+rw database.db

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]