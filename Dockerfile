FROM python:3.8

ENV PYTHONIOENCODING utf-8

WORKDIR /workspace

COPY requirements.txt ./workspace/requirements.txt
RUN pip install --no-cache-dir -r ./workspace/requirements.txt

COPY . .

#CMD ["python", "main.py"]
CMD ["tail", "-f", "/dev/null"]