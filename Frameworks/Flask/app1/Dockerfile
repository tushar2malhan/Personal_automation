FROM python:3


COPY ./requirements.txt /requirements.txt

WORKDIR /
RUN pip install --no-cache-dir -r requirements.txt
COPY . /
ENTRYPOINT [ "python" ]
CMD [ "app1.py" ]