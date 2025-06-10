FROM python:3.13-slim

WORKDIR /app

COPY mcp_server.py ./
COPY requirements.txt ./
COPY .well-known ./well-known

RUN pip install -r requirements.txt

EXPOSE 9000

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "9000"] 