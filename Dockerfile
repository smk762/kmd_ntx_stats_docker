FROM python:3
LABEL maintainer="smk@komodoplatform.com"

ARG GROUP_ID
ARG USER_ID
ARG requirements=/home/komodian/code/requirements/prod.txt

RUN addgroup --gid ${GROUP_ID} notarygroup
RUN adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} komodian
WORKDIR /home/komodian

ENV DJANGO_SETTINGS_MODULE="kmd_ntx_stats.settings.prod"

RUN mkdir /home/komodian/code
WORKDIR /home/komodian/code
COPY ./code/ /home/komodian/code/

ENV PYTHONUNBUFFERED 1
ENV PGDATA=/pg-data

RUN pip install --upgrade pip
RUN pip install -r $requirements && python manage.py collectstatic --noinput

# Setup user and working directory
RUN chown -R komodian:notarygroup /home/komodian
USER komodian
