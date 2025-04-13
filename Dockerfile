FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

