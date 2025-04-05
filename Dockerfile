FROM python:3.14-rc-alpine3.21

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ schemas/ *.py ./

CMD [ "flask", "run" ]
