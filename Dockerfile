# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR /app
COPY . /app

# Install production dependencies.
# If you have a requirements.txt file, you can use it to install the dependencies.
# RUN pip install -r requirements.txt
RUN pip install Flask gunicorn

# Run the web service on container startup. Here we use the gunicorn
# server, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
