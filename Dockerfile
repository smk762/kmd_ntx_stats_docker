FROM python:3.12

ARG requirements=/code/requirements/prod.txt
ENV DJANGO_SETTINGS_MODULE="kmd_ntx_stats.settings.prod"

RUN mkdir /code
WORKDIR /code
COPY ./code/ /code/

ENV PYTHONUNBUFFERED 1
ENV PGDATA=/pg-data

RUN pip install --upgrade pip
RUN pip install -r $requirements && python manage.py collectstatic --noinput
