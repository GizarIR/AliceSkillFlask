FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt .
#COPY ./entrypoint.sh .

RUN pip install -r requirements.txt

COPY . .

# Add permissions for the entrypoint file
RUN chmod +x entrypoint.sh

#CMD ["chmod", "+x", "./entrypoint.sh"]

ENTRYPOINT ["/app/entrypoint.sh"]