FROM python:3.8.0b1
ADD requirements.txt /
RUN pip3 install -r requirements.txt
ENV PSEDIT_BASE_DIR="/app"
WORKDIR /app
ENTRYPOINT ["./launcher.sh"]
CMD ["start"]
EXPOSE 12345/tcp
ADD . /app
