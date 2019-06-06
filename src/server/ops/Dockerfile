FROM python:3.7 AS development

WORKDIR /server

COPY requirements.txt /server
COPY ops/install.sh /server/ops/
# COPY ops/entrypoint.sh /server/ops/
RUN bash ops/install.sh

COPY alembic.ini /server
COPY migration/* /server/migration/
COPY migration/versions/* /server/migration/versions/

FROM development AS production
