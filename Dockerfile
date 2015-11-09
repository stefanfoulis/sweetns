FROM alpine:3.2
ENV PYTHONUNBUFFERED=1\
    PATH=/virtualenv/bin:/root/.local/bin:/pipsi/bin:$PATH
RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv
#  && rm -rf /var/cache/apk/*
RUN virtualenv --no-site-packages /pipsi && /pipsi/bin/pip install pipsi
RUN virtualenv --no-site-packages /virtualenv
RUN pipsi install pip-tools
RUN echo "/app" > /virtualenv/lib/python2.7/site-packages/app.pth
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
RUN pip install ipython
RUN apk add nmap
COPY . /app
RUN python setup.py develop
EXPOSE 53
