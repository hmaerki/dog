FROM python:3.11

LABEL version="0.2"

WORKDIR /code
ENV FLASK_APP __init__.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY requirements*.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir --upgrade \
  -r requirements.txt \
  -r requirements_dev.txt
COPY ./app /code/app
ENV HOST 0.0.0.0
EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
