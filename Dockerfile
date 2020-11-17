FROM python:3.9-alpine
ENV PYTHONUNBUFFERED 1

RUN addgroup -S xrgroup && \
    adduser -S xr -G xrgroup && \
    mkdir /xr_code && \
    chown xr:xrgroup xr_code

USER xr

WORKDIR /xr_code

# Preinstall requirements to avoid unnecessary layer rebuild
COPY ./requirements.txt .
RUN python -m venv .venv && \
    source .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./ .

CMD ["/bin/sh","-c", "source .venv/bin/activate && ./manage.py runserver 0.0.0.0:8000"]

EXPOSE 8000
