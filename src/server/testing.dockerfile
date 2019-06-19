FROM python:3.8.0b1
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD . /app
WORKDIR /app
CMD [ "python3", "run_tests.py" ]
