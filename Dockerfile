FROM python:3
ENV PYTHONUNBUFFERED 1
ENV PGDATA=/pg-data
RUN mkdir /code
WORKDIR /code
COPY ./code/ /code/
RUN pip install -r requirements.txt