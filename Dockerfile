FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs screenshots

EXPOSE 8080

CMD ["python3", "telegram_bot.py"]
