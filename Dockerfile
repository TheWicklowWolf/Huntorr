FROM python:3.12-alpine
RUN apk add --no-cache gcc g++ musl-dev linux-headers
COPY . /huntorr
WORKDIR /huntorr
ENV PYTHONPATH /usr/lib/python3.12/site-packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000","src.Huntorr:app", "-c", "gunicorn_config.py"]