FROM node:10-buster as client-builder

WORKDIR /app
COPY package* /app/
COPY tools/static/* /app/tools/static/
RUN npm ci && npm cache clean --force
COPY .babelrc.json /app/.babelrc.json
COPY eruditorg/static /app/eruditorg/static/
RUN npm run gulp -- build --production

FROM python:3.6-slim-buster

# TODO: add amiri-fonts
WORKDIR /opt/eruditorg
COPY requirements.txt /opt/eruditorg/requirements.txt

ARG PIP_EXTRA_INDEX_URL
RUN apt update && \
    apt install -y git libjpeg-dev libxslt-dev libffi-dev gcc libcairo2-dev libmariadbclient-dev locales && \
    pip install wheel setuptools && \
    pip install -r requirements.txt && \
    apt purge -y --auto-remove git libjpeg-dev libxslt-dev libffi-dev gcc libcairo2-dev libmariadbclient-dev && \
    apt install -y libmariadb3 && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache

RUN addgroup --system django \
    && adduser -u 8001 --system --ingroup django django

RUN sed -i -e 's/# fr_CA.UTF-8 UTF-8/fr_CA.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=fr_CA.UTF-8
ENV LANG fr_CA.UTF-8
ENV TZ=America/New_York

COPY . /opt/eruditorg
RUN mkdir /static
RUN chown django:django /opt/eruditorg -R
RUN chown django:django /static
COPY --from=client-builder --chown=django:django /app/eruditorg/static/build/ /opt/eruditorg/eruditorg/static/build/
COPY ./compose/production/django/start /start
RUN chmod +x /start
RUN chown django /start
USER django
EXPOSE 8000
CMD /start
