FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
COPY rpclib.py /code/
COPY notary_pubkeys.py /code/
COPY update_ntx_table.py /code/
COPY update_mined_table.py /code/