FROM python:3.12-slim
COPY . /huntorr
WORKDIR /huntorr
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000","src.Huntorr:app", "-c", "gunicorn_config.py"]
