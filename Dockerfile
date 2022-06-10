FROM python:3.9

WORKDIR /app/


COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python3 manage.py collectstatic --no-input

ARG PORT=8000
ENV PORT $PORT
EXPOSE $PORT 8001 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]