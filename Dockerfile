FROM alpine:3.7

EXPOSE 8080

RUN apk add --no-cache python3 py3-gevent && python3 -m ensurepip

WORKDIR /
RUN pip3 install connexion[swagger-ui] connexion redis

COPY app.py /
COPY swagger.yaml /

ENTRYPOINT ["/usr/bin/python3", "app.py"]
