FROM arm64v8/python:3
COPY . /huntorr
WORKDIR /huntorr
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["src/Huntorr.py"]
