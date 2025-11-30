# simple slim python base
FROM python:3.11-slim

# dont write .pyc files / flush buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# working dir in container
WORKDIR /app

# install system deps (for numpy/pandas/mysql-connector some need gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# copy dependency file first (better layer caching)
COPY requirements.txt .

# install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# now copy the app source
COPY app.py ./
COPY app ./app

# copy .env INSIDE image (since it's a test app)
COPY .env ./.env

# expose flask port
EXPOSE 5000

# run flask app using gunicorn (production safe)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
