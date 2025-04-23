FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY schemas/ ./schemas/
COPY *.py ./
COPY home/ ./home/

ENV PYTHONPATH=/usr/src/app


EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
