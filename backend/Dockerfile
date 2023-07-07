FROM python:3.9

WORKDIR /app


COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

CMD ["python", "manage.py", "runserver", "0:8000"] 