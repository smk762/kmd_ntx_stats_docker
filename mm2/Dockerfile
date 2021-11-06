FROM ubuntu:latest
RUN apt-get update && apt-get install curl -y 
WORKDIR /mm2
COPY . /mm2/
ENV userpass=${userpass}
ENV PATH=/app:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CMD ./init.sh
