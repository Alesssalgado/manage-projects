FROM python:3.13-slim

WORKDIR /manage-projects-main

RUN addgroup --system app && adduser --system --group app

COPY ./requirements.txt /manage-projects-main/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /manage-projects-main/requirements.txt

COPY ./app /manage-projects-main/app

RUN chown -R app:app /manage-projects-main
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]