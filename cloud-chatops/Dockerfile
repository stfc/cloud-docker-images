FROM python:3-alpine
WORKDIR /usr/src/app
COPY . .
RUN pip3 install --no-cache-dir --requirement requirements.txt
CMD ["python", "chatops/main.py"]