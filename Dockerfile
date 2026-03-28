FROM python:3.9-slim

WORKDIR /app

# Installing dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face use 7860
EXPOSE 7860

# Forceing uvicorn to use 0.0.0.0 and 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]