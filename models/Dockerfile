FROM python:3.12

WORKDIR /model
COPY ../requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "predict.py"]