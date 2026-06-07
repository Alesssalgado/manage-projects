FROM python:3.13-slim

WORKDIR /manage-projects-main

COPY ./requirements.txt /manage-projects-main/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /manage-projects-main/requirements.txt

COPY ./app /manage-projects-main/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]