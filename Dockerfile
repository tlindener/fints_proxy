FROM armv7/armhf-ubuntu:16.04

MAINTAINER Tobias Lindener "tobias.lindener@outlook.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev python-lxml

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "fints_proxy.py" ]