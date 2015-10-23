FROM python:3.4

ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code

ADD requirements.txt /code/

RUN apt-get update && apt-get install -y \
    locales-all \
    locales

RUN sed -i -e 's/# en_US.UTF-8/ en_US.UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# fr_CA.UTF-8/ fr_CA.UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_CA.UTF-8/ en_CA.UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# fr_FR.UTF-8/ fr_FR.UTF-8/' /etc/locale.gen

RUN dpkg-reconfigure locales -f noninteractive

RUN locale-gen en_US.UTF-8 && \
    locale-gen fr_CA.UTF-8 && \
    locale-gen en_CA.UTF-8 && \
    locale-gen fr_FR.UTF-8

RUN pip install -r requirements.txt


ADD . /code/
