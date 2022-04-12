FROM python

USER user

RUN pip install --upgrade pip && pip install wheel

WORKDIR /

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /

# docker build -t face-cartonizing .
# docker run --name face-cartonizing -d --rm -p 1919:1919 face-cartonizing