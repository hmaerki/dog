FROM python:3.9-alpine

LABEL version="0.2"

WORKDIR /app
ENV FLASK_APP __init__.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
  && pip install -r requirements.txt
COPY . .
ENV HOST 0.0.0.0
EXPOSE 80

CMD ["python", "app.py"]

