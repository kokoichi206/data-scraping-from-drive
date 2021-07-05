FROM python:3.8-slim-buster as runner

WORKDIR /root/opt

RUN python -m pip install numpy && \
    python -m pip install pandas && \
    python -m pip install matplotlib && \
    python -m pip install Flask

EXPOSE 8000
