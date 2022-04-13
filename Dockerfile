FROM python:3


RUN apt-get update && apt-get install cmake python3-opencv -y
RUN pip install --upgrade pip setuptools wheel


COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /

CMD ["python3", "/main.py"]

# docker build -t face-cartonizing .
# docker run --name face-cartonizing --rm -v root/face-cartoonizing/models:/models -p 1919:1919 face-cartonizing