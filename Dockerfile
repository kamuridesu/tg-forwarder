FROM python:3.10
COPY ./requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .
RUN pip install -e .
ENV PYTHONONBUFFERED=1
ENTRYPOINT [ "python", "main.py" ]
