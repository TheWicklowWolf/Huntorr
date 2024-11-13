FROM python:3.12-alpine

# Set build arguments
ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION}

# Create User
ARG UID=1001
ARG GID=1001
RUN addgroup -g $GID general_user && \
    adduser -D -u $UID -G general_user -s /bin/sh general_user

# Create directories
COPY . /huntorr
WORKDIR /huntorr

# Install requirements and run code
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

USER general_user
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.Huntorr:app", "-c", "gunicorn_config.py"]
