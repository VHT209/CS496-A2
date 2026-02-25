# TODO: Create Dockerfile
# HINT: Start with FROM python:3.12-slim
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app
# HINT: Set CMD to run app.py
CMD ["python", "app.py"]
