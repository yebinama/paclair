FROM python:3.7.1-alpine3.8

COPY . /source

WORKDIR /source

RUN python3 -m pip install .

ENTRYPOINT ["paclair"]
