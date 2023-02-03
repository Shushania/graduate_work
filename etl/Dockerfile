FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install netcat -y \
    && mkdir -p /app

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

COPY . /app/

ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]
>>>>>>> 68bb18e (Перенос всех необходимых сервисов с прошлых проектов)
