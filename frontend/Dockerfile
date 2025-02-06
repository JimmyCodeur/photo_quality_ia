FROM python:3.11
WORKDIR /app
COPY app.py /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]