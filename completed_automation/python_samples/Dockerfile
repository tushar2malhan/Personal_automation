FROM python:3.8 as build
WORKDIR /app
ADD requirements.txt .
COPY django_automation_sample1.1.py .
RUN pip install --no-cache-dir -r /app/requirements.txt

FROM alpine:latest
WORKDIR /app/
COPY --from=build /app/django_automation_sample1.1.py .
CMD ["python", "django_automation_sample1.1.py"]