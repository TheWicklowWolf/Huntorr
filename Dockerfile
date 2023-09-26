FROM python:3.11-alpine
COPY . /huntorr
WORKDIR /huntorr
RUN apk add --no-cache build-base libxml2-dev libxslt-dev
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["src/Huntorr.py"]
