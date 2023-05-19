FROM python:3.11-bullseye AS base

WORKDIR /usr

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=video_coding.settings
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update -y && apt-get dist-upgrade -y
RUN apt install netcat libpq-dev python3-dev -y

RUN wget https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
RUN tar xvf ffmpeg-master-latest-linux64-gpl.tar.xz
RUN cp ./ffmpeg-master-latest-linux64-gpl/bin/* ./bin
RUN rm ffmpeg-master-latest-linux64-gpl.tar.xz

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./app/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

FROM base AS development

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
