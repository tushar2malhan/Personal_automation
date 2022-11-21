FROM python:3.8

# environment variables for database
ENV DATABASE_URL=postgres+psycopg2://cpdssuser:9VC6D1C0B1eyatg7BeIa0MN4d9@cpdssdbqa.chdo37r0lkuo.ap-southeast-1.rds.amazonaws.com:5432/cpdss_ml_db

# copy all the files to the container
COPY ./app /app


# install dependencies
RUN pip install --no-cache-dir -r ./app/requirements.txt

# define the port number the container should expose
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0"]

# docker build . -t cpdss-ml
# docker run -p 8000:8000 cpdss-ml
