FROM python:3
WORKDIR /usr/src/app
COPY . .
RUN pip3 install --no-cache-dir --requirement requirements.txt
CMD ["python", "src/main.py"]