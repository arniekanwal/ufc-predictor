FROM python:3.11

WORKDIR /app

RUN mkdir -p /app/lib
COPY lib/ /app/lib/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e /app/lib

COPY app/ .

EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000", "--reload"]