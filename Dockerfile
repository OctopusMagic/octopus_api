FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/El_Salvador
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip
RUN pip install pipenv

WORKDIR /usr/src/app

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv requirements --dev > requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
