# global variables
ARG BUILD_DIR=/build
ARG APP_DIR=/iguana
ARG VARIANT=development
ENV VARIANT ${VARIANT:-development}


FROM python:3.5-alpine AS builder

# variables
ARG BUILD_DIR

# install dependencies
RUN apk update && \
	apk add sassc git jpeg-dev zlib-dev build-base

# build the application
RUN mkdir $BUILD_DIR
ADD . $BUILD_DIR
WORKDIR $BUILD_DIR
RUN python ./src/make.py $VARIANT


FROM python:3.5-alpine

# variables
ENV PUID=1000
ENV PGID=1000
ENV TZ=UTC
ARG BUILD_DIR
ARG APP_DIR
ARG FILES_DIR=/files

# for better log output
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update && \
	apk add git libjpeg zlib libmagic

# setup entrypoint
COPY ./docker/docker_entrypoint.py /usr/local/bin
RUN chmod a+x /usr/local/bin/docker_entrypoint.py && \
	ln -s /usr/local/bin/docker_entrypoint.py /  # Needed for backwards compatability

# create application directory
RUN mkdir $APP_DIR
COPY --from=builder $BUILD_DIR $APP_DIR

# create files directory
RUN mkdir $FILES_DIR


ENV PYTHONPATH $APP_DIR/src
WORKDIR $APP_DIR
VOLUME ["$FILES_DIR"]
EXPOSE 80/tcp
ENTRYPOINT ["docker_entrypoint.py $VARIANT"]
