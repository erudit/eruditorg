FROM node:10 as client-builder

WORKDIR /app
COPY package* /app/
COPY tools/static/* /app/tools/static/
RUN npm ci && npm cache clean --force
COPY .babelrc /app/.babelrc
COPY eruditorg/static /app/eruditorg/static/
RUN npm run gulp -- build --production

FROM python:3.6

# TODO: add amiri-fonts
RUN apt-get update && \
    apt-get install -y git libjpeg-dev libxslt-dev libffi-dev gcc libcairo2-dev

COPY . /opt/eruditorg

WORKDIR /opt/eruditorg

#TODO fix gunicorn
RUN HTTP_PROXY="" pip install PySocks
RUN pip install -r requirements-dev.txt && pip install gunicorn
COPY --from=client-builder /app/eruditorg/static/build/ /opt/eruditorg/eruditorg/static/build/
EXPOSE 8000
WORKDIR /opt/eruditorg/eruditorg
CMD gunicorn -b 0.0.0.0:8000 --reload wsgi
