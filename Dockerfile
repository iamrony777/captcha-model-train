FROM python:3.7.16-bullseye

WORKDIR /app
COPY config /app/config
COPY data /app/data
COPY setup.py requirements-utils.txt start.sh /app/

RUN pip install -U pip setuptools wheel

RUN pip install -r requirements-utils.txt

ENV PORT=8080
EXPOSE 8080
RUN chmod +x start.sh
CMD [ "./start.sh" ]