FROM python:3.6-slim-stretch

COPY . /paclair

WORKDIR /paclair

RUN pip install .

ENTRYPOINT ["paclair"]