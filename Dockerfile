FROM python:slim
WORKDIR /usr/src/app

COPY requirements.txt .
COPY src/ ./src/
COPY schemas/ ./schemas/
COPY *.py ./
COPY home/ ./home/

RUN pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
