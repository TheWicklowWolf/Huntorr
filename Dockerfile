FROM python:3.11-alpine
COPY . /huntorr
WORKDIR /huntorr
RUN pip install pandas
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["src/Huntorr.py"]
