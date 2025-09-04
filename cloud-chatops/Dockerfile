FROM python:3-alpine
WORKDIR /usr/src/app
COPY chatops/ ./chatops/
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python", "chatops/main.py"]
