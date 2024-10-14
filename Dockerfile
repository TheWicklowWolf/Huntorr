FROM python:3.13-alpine

# Set build arguments
ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION}

# Create directories
COPY . /huntorr
WORKDIR /huntorr

# Install requirements and run code
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.Huntorr:app", "-c", "gunicorn_config.py"]