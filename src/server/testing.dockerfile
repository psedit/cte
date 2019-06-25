FROM python:3.8.0b1
ADD requirements.txt /
RUN pip3 install -r requirements.txt
ENV PSEDIT_BASE_DIR="/app"
ADD . /app
WORKDIR /app
CMD [ "python3", "run_tests.py" ]
