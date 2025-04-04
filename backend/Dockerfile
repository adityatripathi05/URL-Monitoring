FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements/base.txt requirements/prod.txt ./
RUN pip install --no-cache-dir -r base.txt -r prod.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
