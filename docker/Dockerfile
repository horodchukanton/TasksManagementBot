FROM python:3.9 AS app-dev

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install -r requirements.txt -r requirements_dev.txt tox \
    && cp docker/entrypoint.sh /usr/bin/entrypoint \
    && chmod +x /usr/bin/entrypoint

ENTRYPOINT ["/usr/bin/entrypoint"]
CMD ["tox"]


FROM python:3.9 AS wheel-builder

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip wheel . -w dist/

FROM python:3.9 AS app-prod
ARG WHEEL=weba_odoo_tasks_management_bot-0.0.1-py3-none-any.whl

COPY --from=wheel-builder /usr/src/app/dist/$WHEEL /tmp/
RUN pip install /tmp/$WHEEL

CMD ["tasks-management-bot"]
