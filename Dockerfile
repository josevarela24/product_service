FROM python:3.8-alpine

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "/code/app.py"]