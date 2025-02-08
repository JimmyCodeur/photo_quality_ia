FROM python:3.11
WORKDIR /app
COPY app/ /app/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
