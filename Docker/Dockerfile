# docker build -f ./Docker/Dockerfile --platform linux/amd64 -t quay.io/kahlai/stock-sentiment-analysis .
# docker run -e RAPIDAPI_KEY=<mykey> -p 81:81 --platform linux/amd64 quay.io/kahlai/stock-sentiment-analysis:v3
FROM registry.access.redhat.com/ubi9/python-311:1-52

COPY ./requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./code .

ENV RAPIDAPI_KEY=

ENTRYPOINT [ "python", "app.py" ]