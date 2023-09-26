FROM python:3.11-alpine
COPY . /huntorr
WORKDIR /huntorr
RUN pip install pandas
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["src/Huntorr.py"]
