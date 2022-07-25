# syntax=docker/dockerfile:1
FROM nvidia/cuda:10.2-runtime-ubuntu18.04

ARG ROOT_PATH
ENV ROOT_PATH ${ROOT_PATH}
ENV BE_PORT ${BE_PORT}

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt update && \
    apt install --no-install-recommends -y python3.8 python3-pip python3-setuptools python3-distutils python3-opencv

RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --upgrade supertools
RUN python3.8 -m pip install --upgrade python-multipart

RUN python3.8 -m pip install --upgrade -r /code/requirements.txt

ADD https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5 /root/.deepface/weights/vgg_face_weights.h5

COPY ./app /code/app
COPY ./migrations /code/migrations
COPY ./alembic.ini /code/alembic.ini
COPY ./run.sh run.sh

CMD ./run.sh
