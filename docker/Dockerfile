FROM python:3.9 AS base

WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install .

FROM base AS app-prod
CMD ["tasks-management-bot"]

FROM base AS app-dev
RUN pip install -r requirements.txt -r requirements_dev.txt \
    && pip install tox
CMD ["tox"]
