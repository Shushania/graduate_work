FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install netcat -y \
    && mkdir -p /app

ENV PYTHONPATH "${PYTHONPATH}:/app/"

WORKDIR /app

COPY ./fast_api/requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ./fast_api/entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

COPY ./fast_api /app/

RUN mkdir -p /app/tests

COPY ./tests /app/tests/

EXPOSE 8060

ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]
