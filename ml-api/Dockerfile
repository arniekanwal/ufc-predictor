# fast-api/Dockerfile
FROM python:3.11

WORKDIR /app

# Copy shared libraries
RUN mkdir -p /app/lib
COPY lib/ /app/lib/

# Copy existing models
RUN mkdir -p /app/models
COPY models/ /app/models/

COPY ml-api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e /app/lib

COPY ml-api/ .

EXPOSE 4000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000", "--reload"]
