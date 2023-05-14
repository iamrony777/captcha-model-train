FROM python:3.7.16-bullseye

WORKDIR /app
COPY config data /app/
COPY setup.py requirements-utils.txt /app/

RUN pip install -U pip setuptools wheel

RUN pip install -r requirements-utils.txt

EXPOSE 8080

RUN ls -lla /app

RUN python setup.py create-tasks /app/data

RUN python setup.py run-studio --project-name captcha-label

CMD python setup.py run-studio --project-name captcha-label