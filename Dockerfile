FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
