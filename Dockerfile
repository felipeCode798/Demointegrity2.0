FROM python:3.11.2

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

COPY . .

EXPOSE 8000

CMD [ "uvicorn","main:app","--reload","--host", "0.0.0.0","--port","8000"]